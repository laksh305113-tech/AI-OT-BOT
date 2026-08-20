"""Password hashing and JWT helpers for the AI-OT prototype."""
from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.config import get_settings

PASSWORD_HASHER = PasswordHash.recommended()
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return PASSWORD_HASHER.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires_at}, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, get_settings().jwt_secret_key, algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Token has no subject")
        return int(subject)
    except (InvalidTokenError, TypeError, ValueError) as error:
        raise ValueError("Invalid or expired access token") from error
