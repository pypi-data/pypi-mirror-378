# gisweb_tenants/fastapi_deps.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from fastapi import Request, Depends, HTTPException
from redis.asyncio import Redis
from gisweb_tenants.registry import TenantsRegistry
from gisweb_tenants.security_bff import KcTenantCfg, KcBffSession
from gisweb_tenants.crypto import AeadBox

@dataclass
class FastAPIDeps:
    registry: TenantsRegistry
    redis: Redis
    aead_box: AeadBox | None
    tenant_header: str
    default_tenant: str
    # default KC (override per-tenant da tenants.yml)
    kc_base: str
    kc_realm: str
    kc_client_id: str
    public_url: str
    session_cookie: str = "__Host-session"
    kc_session_ttl: int = 60*60*24*7
    kc_refresh_safety: int = 60

    def kc_cfg_for(self, tenant: str) -> KcTenantCfg:
        rec = self.registry.get(tenant).config or {}
        kc = rec.get("keycloak") or {}
        return KcTenantCfg(
            base = kc.get("base", self.kc_base),
            realm = kc.get("realm", self.kc_realm),
            client_id = kc.get("client_id", self.kc_client_id),
            public_url = kc.get("public_url", self.public_url),
            session_cookie = kc.get("session_cookie", self.session_cookie),
            session_ttl_seconds = int(kc.get("session_ttl_seconds", self.kc_session_ttl)),
            refresh_safety_seconds = int(kc.get("refresh_safety_seconds", self.kc_refresh_safety)),
        )

    def bff_for(self, tenant: str, kc_cfg: KcTenantCfg) -> KcBffSession:
        return KcBffSession(redis=self.redis, tenant=tenant, cfg=kc_cfg, aead=self.aead_box)


# -------- Dependency helpers (riusabili nei router) --------

def get_deps(request: Request) -> FastAPIDeps:
    deps: FastAPIDeps = request.app.state.deps  # popolato nel lifespan
    return deps

def get_registry(deps: FastAPIDeps = Depends(get_deps)) -> TenantsRegistry:
    # ricarica se il file è cambiato; il Registry già lo gestisce
    return deps.registry

def get_tenant(request: Request, deps: FastAPIDeps = Depends(get_deps)) -> str:
    tenant = request.headers.get(deps.tenant_header, deps.default_tenant).strip().lower()
    if not deps.registry.exists(tenant):
        raise HTTPException(status_code=404, detail="Tenant sconosciuto")
    return tenant

def get_kc_cfg(tenant: str = Depends(get_tenant), deps: FastAPIDeps = Depends(get_deps)) -> KcTenantCfg:
    return deps.kc_cfg_for(tenant)

def get_bff_session(
    tenant: str = Depends(get_tenant),
    kc_cfg: KcTenantCfg = Depends(get_kc_cfg),
    deps: FastAPIDeps = Depends(get_deps),
) -> KcBffSession:
    return deps.bff_for(tenant, kc_cfg)
