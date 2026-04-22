from fastapi import APIRouter

from app.dependencies.dependencies import AuthServiceDep
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenPair,
    RefreshRequest,
    AccessTokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenPair, status_code=201)
async def register(data: UserRegister, service: AuthServiceDep):
    return await service.register(data)


@router.post("/login", response_model=TokenPair)
async def login(data: UserLogin, service: AuthServiceDep):
    return await service.login(data)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(data: RefreshRequest, service: AuthServiceDep):
    return await service.refresh(data.refresh_token)