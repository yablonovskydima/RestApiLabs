from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.core.rate_limiter import check_rate_limit

from app.core.security import decode_token
from app.db.session import get_session
from app.models.users import User
from app.repository.book_repository import BookRepository
from app.repository.auth_repository import AuthRepository
from app.service.auth_service import AuthService
from app.service.book_service import BookService


def get_book_service(session: AsyncSession = Depends(get_session)) -> BookService:
    repository = BookRepository(session)
    return BookService(repository)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    repository = AuthRepository(session)
    return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


_bearer = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(_bearer),
        session: AsyncSession = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = decode_token(auth.removeprefix("Bearer "))
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None
    except JWTError:
        return None

OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]


async def rate_limit(request: Request) -> None:
    auth = request.headers.get("Authorization", "")

    if auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ")
        try:
            decode_token(token)
            key = f"rl:auth:{token[:32]}"
            await check_rate_limit(key, limit=10)
            return
        except JWTError:
            pass

    ip = request.client.host
    await check_rate_limit(f"rl:anon:{ip}", limit=2)

RateLimitDep = Annotated[None, Depends(rate_limit)]