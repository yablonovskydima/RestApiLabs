from fastapi import HTTPException
from jose import JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.users import User
from app.repository.auth_repository import AuthRepository
from app.schemas.auth import UserRegister, UserLogin, TokenPair, AccessTokenResponse


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register(self, data: UserRegister) -> TokenPair:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=409, detail="User with this email already exists")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
        )
        user = await self.repository.create(user)
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def login(self, data: UserLogin) -> TokenPair:
        user = await self.repository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is disabled")
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> AccessTokenResponse:
        credentials_exception = HTTPException(status_code=401, detail="Invalid or expired refresh token")
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise credentials_exception
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        user = await self.repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise credentials_exception
        return AccessTokenResponse(access_token=create_access_token(str(user.id)))