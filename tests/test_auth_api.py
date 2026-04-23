import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.api.auth import register, login, refresh
from app.schemas.auth import UserRegister, UserLogin, RefreshRequest, TokenPair, AccessTokenResponse


def make_token_pair() -> TokenPair:
    return TokenPair(
        access_token="access.token.here",
        refresh_token="refresh.token.here",
    )


def make_access_token() -> AccessTokenResponse:
    return AccessTokenResponse(access_token="new.access.token")


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.mark.asyncio
async def test_register_success(mock_service):
    mock_service.register.return_value = make_token_pair()

    data = UserRegister(email="test@example.com", username="testuser", password="Password1")
    result = await register(data=data, service=mock_service)

    assert result.access_token == "access.token.here"
    assert result.refresh_token == "refresh.token.here"
    assert result.token_type == "bearer"
    mock_service.register.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_register_duplicate_email(mock_service):
    mock_service.register.side_effect = HTTPException(status_code=409, detail="User with this email already exists")

    data = UserRegister(email="test@example.com", username="testuser", password="Password1")

    with pytest.raises(HTTPException) as exc:
        await register(data=data, service=mock_service)

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_login_success(mock_service):
    mock_service.login.return_value = make_token_pair()

    data = UserLogin(email="test@example.com", password="Password1")
    result = await login(data=data, service=mock_service)

    assert result.access_token == "access.token.here"
    assert result.refresh_token == "refresh.token.here"
    mock_service.login.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_login_invalid_credentials(mock_service):
    mock_service.login.side_effect = HTTPException(status_code=401, detail="Invalid email or password")

    data = UserLogin(email="test@example.com", password="WrongPass1")

    with pytest.raises(HTTPException) as exc:
        await login(data=data, service=mock_service)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_success(mock_service):
    mock_service.refresh.return_value = make_access_token()

    data = RefreshRequest(refresh_token="valid.refresh.token")
    result = await refresh(data=data, service=mock_service)

    assert result.access_token == "new.access.token"
    assert result.token_type == "bearer"
    mock_service.refresh.assert_awaited_once_with("valid.refresh.token")


@pytest.mark.asyncio
async def test_refresh_invalid_token(mock_service):
    mock_service.refresh.side_effect = HTTPException(status_code=401, detail="Invalid or expired refresh token")

    data = RefreshRequest(refresh_token="invalid.token")

    with pytest.raises(HTTPException) as exc:
        await refresh(data=data, service=mock_service)

    assert exc.value.status_code == 401