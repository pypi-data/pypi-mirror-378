# gisweb_tenants/oidc/helpers.py
from __future__ import annotations
import secrets
from typing import Tuple
from authlib.oauth2.rfc7636 import create_s256_code_challenge
from gisweb_tenants.security_bff import KcBffSession

async def prep_oidc_temp_state(
    bff: KcBffSession,
    *,
    return_to: str = "/",
    ttl_seconds: int = 600,
) -> Tuple[str, str, str, str]:
    """
    Prepara stato temporaneo per OIDC + PKCE e lo salva in Redis via BFF.

    Ritorna:
      - state: anti-CSRF per il redirect OIDC
      - nonce: legato all'id_token
      - code_verifier: segreto PKCE lato server
      - code_challenge: derivato S256 per la request /auth

    Persistenza:
      bff.put_state(state, {"nonce", "code_verifier", "return_to"}, ttl=ttl_seconds)
    """
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(64)        # OK per PKCE
    code_challenge = create_s256_code_challenge(code_verifier)

    await bff.put_state(
        state,
        {"nonce": nonce, "code_verifier": code_verifier, "return_to": return_to},
        ttl=ttl_seconds,
    )
    return state, nonce, code_verifier, code_challenge
