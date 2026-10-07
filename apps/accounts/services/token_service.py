"""Emite y abre JWT cifrados con JWE A256GCM."""
import base64
import json
import os
from datetime import UTC, datetime, timedelta

from jwcrypto import jwe, jwk

from apps.accounts.exceptions import AppError


def _key() -> jwk.JWK:
    """Carga una clave simétrica de exactamente 32 bytes."""
    raw = os.getenv("JWT_ENCRYPTION_KEY", "")
    try:
        decoded = base64.b64decode(raw, validate=True)
    except ValueError as exc:
        raise AppError("configuración de token inválida", 500) from exc
    if len(decoded) != 32:
        raise AppError("configuración de token inválida", 500)
    encoded = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode()
    return jwk.JWK(kty="oct", k=encoded)


def ttl() -> timedelta:
    """Obtiene la duración de sesión dentro de límites seguros."""
    try:
        minutes = int(os.getenv("JWT_TTL_MINUTES", "15"))
    except ValueError:
        minutes = 15
    return timedelta(minutes=min(max(minutes, 1), 1440))


def issue(user_id: int) -> str:
    """Crea un JWT cifrado que contiene únicamente id y tiempos."""
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + ttl()).timestamp()),
    }
    token = jwe.JWE(
        json.dumps(claims).encode(),
        protected={"alg": "dir", "enc": "A256GCM", "typ": "JWT"},
    )
    token.add_recipient(_key())
    return token.serialize(compact=True)


def read(compact: str) -> int:
    """Descifra un token vigente y retorna el id del usuario."""
    try:
        token = jwe.JWE()
        token.deserialize(compact, key=_key())
        claims = json.loads(token.payload)
        if datetime.now(UTC).timestamp() >= int(claims["exp"]):
            raise ValueError("expired")
        return int(claims["sub"])
    except (KeyError, TypeError, ValueError, jwe.InvalidJWEData) as exc:
        raise AppError("la sesion vencio", 401) from exc
