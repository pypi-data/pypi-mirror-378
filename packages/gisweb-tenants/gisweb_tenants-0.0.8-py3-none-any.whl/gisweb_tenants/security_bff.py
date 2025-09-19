# gisweb_tenants/security_bff.py
from __future__ import annotations
import base64
import json, time, secrets
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from fastapi import HTTPException, Response
from redis.asyncio import Redis
from .crypto import AeadBox

class SessionStoreUnavailable(HTTPException):
    def __init__(self): super().__init__(status_code=503, detail="Session store (Redis) non disponibile")

@dataclass(frozen=True)
class KcTenantCfg:
  base: str
  realm: str
  client_id: str
  public_url: str
  session_cookie: str = "__Host-session"
  session_ttl_seconds: int = 60*60*24*7
  refresh_safety_seconds: int = 60

  @property
  def issuer(self) -> str: return f"{self.base}/realms/{self.realm}"
  @property
  def auth_url(self) -> str: return f"{self.issuer}/protocol/openid-connect/auth"
  @property
  def token_url(self) -> str: return f"{self.issuer}/protocol/openid-connect/token"
  @property
  def logout_url(self) -> str: return f"{self.issuer}/protocol/openid-connect/logout"
  @property
  def jwks_url(self) -> str: return f"{self.issuer}/protocol/openid-connect/certs"

class KcBffSession:
  """
  Sessione BFF per-tenant: conserva token OIDC di Keycloak in Redis (cifrati),
  più metadati utente. Nessun JWT “di casa”: il browser vede solo un cookie opaco.
  """
  def __init__(self, *, redis: Redis, tenant: str, cfg: KcTenantCfg, aead: Optional[AeadBox] = None):
    self.r = redis
    self.tenant = tenant.strip().lower()
    self.cfg = cfg
    self.aead = aead

  # chiavi Redis per-tenant
  def _k(self, *parts: str) -> str: return "kc:%s:%s" % (self.tenant, ":".join(parts))
  def _k_state(self, state: str) -> str:   return self._k("state", state)
  def _k_session(self, sid: str) -> str:   return self._k("sid", sid)

  def _enc(self, b: bytes, aad: bytes) -> str:
      if not self.aead:
          return b.decode("ascii")  # i JWT sono ASCII-safe
      ct: bytes = self.aead.encrypt(b, aad=aad)   # <- bytes
      return base64.urlsafe_b64encode(ct).decode("ascii")  # <- str JSON-safe

  def _dec(self, s: str, aad: bytes) -> bytes:
      if not self.aead:
          return s.encode("ascii")
      ct = base64.urlsafe_b64decode(s.encode("ascii"))
      return self.aead.decrypt(ct, aad=aad)

  async def put_state(self, state: str, data: Dict[str, Any], ttl: int = 600):
    try:
      await self.r.set(self._k_state(state), json.dumps(data), ex=ttl)
    except Exception: raise SessionStoreUnavailable()

  async def pop_state(self, state: str) -> Optional[Dict[str, Any]]:
    key = self._k_state(state)
    pipe = self.r.pipeline()
    await pipe.get(key); await pipe.delete(key)
    got, _ = await pipe.execute()
    return json.loads(got) if got else None

  async def create_session(self, *, sid: str, sub: str, token_res: dict, claims: dict) -> Optional[Dict[str, Any]]:
      """
      Persisti la sessione a partire dalla risposta /token (authorization_code o refresh_token).
      Tutti i valori salvati sono JSON-safe (str/int/list), i token sono cifrati+base64 via _enc.
      """
      try:
          now = int(time.time())
          exp = now + int(token_res.get("expires_in", 60))
          rex_raw = int(token_res.get("refresh_expires_in", 0) or 0)
          rex = now + rex_raw if rex_raw > 0 else 0

          # token -> str (cifrati e base64 urlsafe da _enc)
          at_raw = token_res["access_token"]                      # sempre presente
          rt_raw = token_res.get("refresh_token") or ""
          it_raw = token_res.get("id_token") or ""

          at = self._enc(at_raw.encode("ascii"), aad=f"{self.tenant}|{sid}|AT".encode("ascii"))
          rt = self._enc(rt_raw.encode("ascii"), aad=f"{self.tenant}|{sid}|RT".encode("ascii")) if rt_raw else ""
          it = self._enc(it_raw.encode("ascii"), aad=f"{self.tenant}|{sid}|ID".encode("ascii")) if it_raw else ""

          # claims -> solo campi stringa utili
          username = claims.get("preferred_username")
          email = claims.get("email")
          name = claims.get("name")

          roles = self._extract_roles(claims)
          if isinstance(roles, set):
              roles = list(roles)

          session = {
              "tenant": self.tenant,
              "sid": sid,
              "sub": sub,
              "client_id": self.cfg.client_id,
              "exp": int(exp),
              "refresh_exp": int(rex),          # 0 se non fornito
              "access_token": at,
              "refresh_token": rt,
              "id_token": it,
              "username": username,
              "email": email,
              "name": name,
              "roles": roles or [],
          }

          # TTL: usa refresh_expires_in se c'è, altrimenti session_ttl_seconds
          ttl = self.cfg.session_ttl_seconds
          if rex > now:
              ttl = max(60, min(self.cfg.session_ttl_seconds, rex - now))

          await self.r.set(self._k_session(sid), json.dumps(session, ensure_ascii=False), ex=int(ttl))
          return session
          
      except Exception:
          # Se vuoi essere più fine, intercetta RedisError separatamente
          raise SessionStoreUnavailable()


  def _extract_roles(self, claims: dict) -> list[str]:
    rr = (claims.get("realm_access") or {}).get("roles", []) or []
    cr = (claims.get("resource_access") or {}).get(self.cfg.client_id, {}).get("roles", []) or []
    return list({*rr, *cr})

  async def get_session(self, sid: str) -> dict:
    raw = await self.r.get(self._k_session(sid))
    if not raw: raise HTTPException(status_code=401, detail="Sessione scaduta")
    return json.loads(raw)

  async def needs_refresh(self, sess: dict) -> bool:
    return int(time.time()) >= int(sess["exp"]) - self.cfg.refresh_safety_seconds

  async def update_tokens(self, sid: str, token_res: dict):
    s = await self.get_session(sid)
    now = int(time.time())
    s["exp"] = now + int(token_res.get("expires_in", 60))
    rex = int(token_res.get("refresh_expires_in", 0) or 0)
    if rex: s["refresh_exp"] = now + rex

    s["access_token"]  = self._enc(token_res["access_token"].encode(),   aad=f"{self.tenant}|{sid}|AT".encode())
    if token_res.get("refresh_token"):
      s["refresh_token"] = self._enc(token_res["refresh_token"].encode(), aad=f"{self.tenant}|{sid}|RT".encode())
    await self.r.set(self._k_session(sid), json.dumps(s), ex=max(60, (s.get("refresh_exp", now) - now)))

  async def delete_session(self, sid: str):
    await self.r.delete(self._k_session(sid))

  # helper per estrarre i token decifrati lato server
  def read_access_token(self, sess: dict) -> str:
    return self._dec(sess["access_token"], aad=f"{self.tenant}|{sess['sid']}|AT".encode()).decode()

  def read_refresh_token(self, sess: dict) -> Optional[str]:
    rt = sess.get("refresh_token") or ""
    if not rt: return None
    return self._dec(rt, aad=f"{self.tenant}|{sess['sid']}|RT".encode()).decode()


def set_session_cookie(response: Response, kc: KcTenantCfg, sid: str, sess: dict, *, domain: str | None = None) -> None:
    """
    Imposta/renova il cookie con Max-Age coerente con la sessione.
    Se hai refresh_exp, limita il Max-Age a quello; altrimenti usa kc.session_ttl_seconds.
    """
    now = int(time.time())
    # calcola quanto resta alla scadenza del refresh, altrimenti usa TTL di default
    if (rex := int(sess.get("refresh_exp", 0))) > now:
        max_age = max(60, min(kc.session_ttl_seconds, rex - now))
    else:
        max_age = kc.session_ttl_seconds

    response.set_cookie(
        key=kc.session_cookie,
        value=sid,
        path="/",
        max_age=int(max_age),         # ← fondamentale per rolling cookie
        httponly=True,
        secure=True,
        samesite="lax",
        domain=domain
    )

def clear_session_cookie(response: Response, kc: KcTenantCfg, *, domain: str | None = None):
    # Starlette imposta Max-Age=0 ed Expires nel passato
    response.delete_cookie(
        key=kc.session_cookie,
        path="/",
        domain=domain    
    )
    
def sanitize_return_to(rt: str, kc: KcTenantCfg) -> str:
    # Evita open-redirect: consenti solo path locali o stessa origin di public_url
    if not rt:
        return "/"
    u = urlparse(rt)
    if not u.netloc:  # path relativo tipo "/dashboard"
        return u.geturl() or "/"
    base = urlparse(kc.public_url)
    same_origin = (u.scheme, u.netloc) == (base.scheme, base.netloc)
    return u.geturl() if same_origin else "/"

