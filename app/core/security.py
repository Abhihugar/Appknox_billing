from argon2 import PasswordHasher
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from app.core import exceptions
from app.core.config import settings
from app.core.token import decode_jwt
from app.db import async_session
from app.models import User


RESET_PASSWORD_TOKEN_AUDIENCE = "user:reset"
VERIFY_USER_TOKEN_AUDIENCE = "user:verify"
LOGIN_VERIFICATION_AUDIENCE = "user:login"

ph: PasswordHasher = PasswordHasher(
    time_cost=settings.ARGON2_ITERATION_COUNT,
    memory_cost=settings.ARGON2_HASH_MEMORY,
    parallelism=settings.ARGON2_PARALLELISM,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password, hashed_password):
    """
    Compare the input password with the stored and hashed password.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except Exception as e:
        return False


def get_hashed_password(password):
    """
    Hash the plain text password and return it
    """
    return ph.hash(password)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode the token and validate the user
    """
    try:
        payload = decode_jwt(
            token,
            secret=settings.SECRET_KEY,
            audience=[LOGIN_VERIFICATION_AUDIENCE]
        )
    except PyJWTError:
        raise exceptions.InvalidToken()

    username: str = payload.get("sub")
    if username is None:
        raise exceptions.NotAuthorized()

    async with async_session() as session:
        user: User | None = await User.get_by_username(
            session=session, username=username
        )

    if user is None:
        raise exceptions.NotAuthorized()
    return user