from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pydantic import SecretStr

from app.core.config import settings

SecretType = str | SecretStr


def _get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
        data: dict,
        secret: SecretType,
        lifetime_seconds: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        algorithm: str = settings.HASHING_ALGORITHM,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
        encoded_jwt: str,
        secret: SecretType,
        audience: list[str],
        algorithms=None,
) -> dict[str, Any]:
    if algorithms is None:
        algorithms = [settings.HASHING_ALGORITHM]
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
