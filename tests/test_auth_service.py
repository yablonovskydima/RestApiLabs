import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.service.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin
from app.models.users import User
from app.core.security import hash_password, create_refresh_token


def make_user(**kwargs) -> User:
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": hash_password("Password1"),
        "is_active": True,
    }
    user = MagicMock(spec=User)
    for k, v in {**defaults, **kwargs}.items():
        setattr(user, k, v)
    return user


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return AuthService(repository=mock_repo)


@pytest.mark.asyncio
async def test_register_success(service, mock_repo):
    mock_repo.get_by_email.return_value = None
    user = make_user()
    mock_repo.create.return_value = user

    data = UserRegister(email="test@example.com", username="testuser", password="Password1")
    result = await service.register(data)

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"
    mock_repo.get_by_email.assert_awaited_once_with("test@example.com")
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email(service, mock_repo):
    mock_repo.get_by_email.return_value = make_user()

    data = UserRegister(email="test@example.com", username="testuser", password="Password1")

    with pytest.raises(HTTPException) as exc:
        await service.register(data)

    assert exc.value.status_code == 409
    assert "already exists" in exc.value.detail
    mock_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_login_success(service, mock_repo):
    user = make_user()
    mock_repo.get_by_email.return_value = user

    data = UserLogin(email="test@example.com", password="Password1")
    result = await service.login(data)

    assert result.access_token
    assert result.refresh_token


@pytest.mark.asyncio
async def test_login_wrong_password(service, mock_repo):
    user = make_user()
    mock_repo.get_by_email.return_value = user

    data = UserLogin(email="test@example.com", password="WrongPass1")

    with pytest.raises(HTTPException) as exc:
        await service.login(data)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(service, mock_repo):
    mock_repo.get_by_email.return_value = None

    data = UserLogin(email="noone@example.com", password="Password1")

    with pytest.raises(HTTPException) as exc:
        await service.login(data)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(service, mock_repo):
    user = make_user(is_active=False)
    mock_repo.get_by_email.return_value = user

    data = UserLogin(email="test@example.com", password="Password1")

    with pytest.raises(HTTPException) as exc:
        await service.login(data)

    assert exc.value.status_code == 403
    assert "disabled" in exc.value.detail


@pytest.mark.asyncio
async def test_refresh_success(service, mock_repo):
    user = make_user()
    mock_repo.get_by_id.return_value = user

    refresh_token = create_refresh_token(str(user.id))
    result = await service.refresh(refresh_token)

    assert result.access_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token(service, mock_repo):
    with pytest.raises(HTTPException) as exc:
        await service.refresh("invalid.token.here")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token(service, mock_repo):
    from app.core.security import create_access_token
    user = make_user()
    access_token = create_access_token(str(user.id))

    with pytest.raises(HTTPException) as exc:
        await service.refresh(access_token)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_inactive_user(service, mock_repo):
    user = make_user(is_active=False)
    mock_repo.get_by_id.return_value = user

    refresh_token = create_refresh_token(str(user.id))

    with pytest.raises(HTTPException) as exc:
        await service.refresh(refresh_token)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_user_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    refresh_token = create_refresh_token(str(uuid.uuid4()))

    with pytest.raises(HTTPException) as exc:
        await service.refresh(refresh_token)

    assert exc.value.status_code == 401