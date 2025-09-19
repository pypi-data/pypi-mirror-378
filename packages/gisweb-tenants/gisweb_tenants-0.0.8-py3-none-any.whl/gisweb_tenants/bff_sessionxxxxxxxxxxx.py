# bff_session.py
from __future__ import annotations
import json, time
from dataclasses import dataclass
from typing import Optional
from redis.asyncio import Redis
from fastapi import HTTPException

class SessionStoreUnavailable(HTTPException):
    def __init__(self): super().__init__(status_code=503, detail="Session store (Redis) non disponibile")

@dataclass(frozen=True)
class KcBffConfig:
    tenant: str = "istanze"
    client_id: str = "e463"                 # client KC usato dal BFF
    access_ttl_safety: int = 30                 # soglia per refresh anticipato (sec)
    session_ttl_seconds: int = 60*60*24*7       # TTL hard della sessione in Redis (oltre a refresh_expires_in)
    encrypt: callable | None = None             # funzione bytes->str
    decrypt: callable | None = None             # funzione str->bytes

class KcBffSession:
    """
    Sessione BFF: conserva token Keycloak per utente (per client) e dati utente.
    Non emette JWT propri; espone metodi per salvare/ruotare/revocare.
    """
    def __init__(self, *, redis: Redis, cfg: KcBffConfig):
        self.r = redis
        self.cfg = cfg
        self.t = cfg.tenant.strip().lower()

    # chiavi Redis
    def _k_userinfo(self, sub: str) -> str:     return f"kc:{self.t}:user:{sub}:info"
    def _k_session(self, sid: str) -> str:      return f"kc:{self.t}:sid:{sid}:session"
    def _k_refresh_revoked(self) -> str:        return f"kc:{self.t}:revoked_rt"

    # util
    def _enc(self, b: bytes) -> str:
        return self.cfg.encrypt(b) if self.cfg.encrypt else b.decode()
    def _dec(self, s: str) -> bytes:
        return self.cfg.decrypt(s) if self.cfg.decrypt else s.encode()

    async def save_from_token_response(self, *, sub: str, sid: str, token_res: dict, profile: dict | None = None):
        """
        Salva tokens appena ricevuti da KC /token (grant=authorization_code o refresh_token).
        token_res: {access_token, refresh_token, id_token, expires_in, refresh_expires_in, ...}
        """
        try:
            now = int(time.time())
            at = token_res["access_token"]; rt = token_res.get("refresh_token", "")
            it = token_res.get("id_token", "")
            exp = now + int(token_res.get("expires_in", 60))
            r_exp = now + int(token_res.get("refresh_expires_in", 0) or 0)

            # profilo base nel carrello (override se passato)
            userinfo = profile or {}
            userinfo.update({"sub": sub, "sid": sid})

            # session blob
            session = {
                "sub": sub,
                "sid": sid,
                "client_id": self.cfg.client_id,
                "exp": exp,
                "refresh_exp": r_exp,
                "access_token": self._enc(at.encode()),
                "refresh_token": self._enc(rt.encode()) if rt else "",
                "id_token": self._enc(it.encode()) if it else "",
                "roles": self._extract_roles_from_id_token(profile, token_res),
            }

            # TTL sessione: almeno fino al refresh_expires_in, cappata da session_ttl_seconds
            ttl = max(60, min(self.cfg.session_ttl_seconds, (r_exp - now) if r_exp else self.cfg.session_ttl_seconds))

            await self.r.set(self._k_session(sid), json.dumps(session), ex=ttl)
            if userinfo:
                await self.r.set(self._k_userinfo(sub), json.dumps(userinfo), ex=ttl)
        except Exception:
            raise SessionStoreUnavailable()

    def _extract_roles_from_id_token(self, profile: dict | None, token_res: dict) -> list[str]:
        # se hai già decodificato id_token o ottenuto claims, mappa ruoli qui
        # fallback: nessun ruolo
        claims = profile or {}
        rr = (claims.get("realm_access") or {}).get("roles", []) or []
        cr = (claims.get("resource_access") or {}).get(self.cfg.client_id, {}).get("roles", []) or []
        return list({*rr, *cr})

    async def get_session(self, sid: str) -> dict:
        raw = await self.r.get(self._k_session(sid))
        if not raw: raise HTTPException(status_code=401, detail="Sessione scaduta")
        return json.loads(raw)

    async def needs_refresh(self, sess: dict) -> bool:
        return int(time.time()) >= int(sess["exp"]) - self.cfg.access_ttl_safety

    async def update_tokens(self, sid: str, new_token_res: dict):
        s = await self.get_session(sid)
        await self.save_from_token_response(sub=s["sub"], sid=sid, token_res=new_token_res)

    async def revoke_session(self, sid: str, refresh_jti: str | None = None):
        try:
            # blacklist eventuale refresh (opzionale)
            if refresh_jti:
                await self.r.sadd(self._k_refresh_revoked(), refresh_jti)
            await self.r.delete(self._k_session(sid))
        except Exception:
            raise SessionStoreUnavailable()

    async def backchannel_logout(self, sid: str):
        """Chiamata dal logout backchannel di Keycloak: invalida tutte le sessioni con quel sid."""
        await self.r.delete(self._k_session(sid))
