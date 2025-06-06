from fastapi import (
    Depends,
    APIRouter,
)
from fastapi.security import OAuth2PasswordRequestForm
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import user
from app.core import exceptions
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_hashed_password,
    LOGIN_VERIFICATION_AUDIENCE,
    RESET_PASSWORD_TOKEN_AUDIENCE,
)
from app.core.token import generate_jwt, decode_jwt
from app.db import get_session
from app.models import User

auth_router = APIRouter(
    prefix="/auth",
)


@auth_router.post("/signup", response_model=user.UserRead)
async def register_user(
        user: user.UserCreate, session: AsyncSession = Depends(get_session)
):
    user_details = user.dict()
    user: User | None = None
    user = await User.get_by_email(
        session=session,
        email=user_details.get("email")
    )
    if user:
        raise exceptions.DuplicateEntry(detail="Email already exists")

    user_details["password"] = get_hashed_password(user_details.get("password"))
    _user = await User.create(session, **user_details)
    await session.commit()
    await session.refresh(_user)
    return _user


@auth_router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session),
):
    email = form_data.username
    user: User = await User.get_by_email(session=session, email=email)

    if not user or not verify_password(form_data.password, user.password):
        raise exceptions.NotAuthorized()

    access_token = generate_jwt(
        data={"sub": user.username, "aud": LOGIN_VERIFICATION_AUDIENCE},
        secret=settings.SECRET_KEY,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_email": user.email
    }


@auth_router.post("/forgot_password", response_model=None)
async def forgot_password(
        request_data: user.ForgotPassword,
        session: AsyncSession = Depends(get_session),
):
    user: User = await User.get_by_email(session=session, email=request_data.email)

    if user is None or user.is_blocked:
        raise exceptions.InvalidUser()

    token_data = {
        "sub": str(user.id),
        "password_fgpt": get_hashed_password(user.password),
        "aud": RESET_PASSWORD_TOKEN_AUDIENCE,
    }

    try:
        token = generate_jwt(
            token_data,
            settings.SECRET_KEY,
            settings.USER_PWD_RESET_TOKEN_EXPIRE_MINUTES * 60,
        )
    except Exception:
        raise exceptions.InternalError("Error while generating token")

    return {"token": token}


@auth_router.post("/reset_password", response_model=user.UserRead)
async def reset_password(
        reset_data: user.ResetPassword,
        session: AsyncSession = Depends(get_session)
):
    try:
        data = decode_jwt(
            reset_data.token,
            secret=settings.SECRET_KEY,
            audience=[RESET_PASSWORD_TOKEN_AUDIENCE],
        )
    except PyJWTError:
        raise exceptions.InvalidToken()

    try:
        user_id = data["sub"]
        password_fingerprint = data["password_fgpt"]
    except KeyError:
        raise exceptions.InvalidToken()

    try:
        user_id = int(user_id)
    except Exception:
        raise exceptions.InvalidToken()

    user: User = await User.get(session, user_id)

    valid_password_fingerprint = verify_password(
        user.password, password_fingerprint
    )

    if not valid_password_fingerprint:
        raise exceptions.InvalidToken()

    if not user.is_active or user.is_blocked:
        raise exceptions.InvalidUser()

    hashed_password = get_hashed_password(reset_data.new_password)
    await User.update(session, user.id, password=hashed_password)
    await session.refresh(user)
    return user
