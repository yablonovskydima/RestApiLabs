import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.repository.auth_repository import AuthRepository
from app.models.users import User


def make_user(**kwargs) -> User:
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashed_pw",
        "is_active": True,
    }
    user = MagicMock(spec=User)
    for k, v in {**defaults, **kwargs}.items():
        setattr(user, k, v)
    return user


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return AuthRepository(session=mock_session)


@pytest.mark.asyncio
async def test_get_by_email_found(repo, mock_session):
    user = make_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_email("test@example.com")

    assert result is user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_email("noone@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_found(repo, mock_session):
    user = make_user()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id(str(user.id))

    assert result is user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id(str(uuid.uuid4()))

    assert result is None


@pytest.mark.asyncio
async def test_create_adds_and_commits(repo, mock_session):
    user = make_user()

    result = await repo.create(user)

    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)
    assert result is user


@pytest.mark.asyncio
async def test_create_returns_refreshed_user(repo, mock_session):
    user = make_user(email="new@example.com")

    result = await repo.create(user)

    assert result.email == "new@example.com"