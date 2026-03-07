import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.book_repository import BookRepository
from app.enums.book_status import BookStatus
from app.models.book_data import Book


def make_mock_book(**kwargs) -> MagicMock:
    book = MagicMock(spec=Book)
    book.id = kwargs.get("id", uuid4())
    book.title = kwargs.get("title", "Test Book")
    book.author = kwargs.get("author", "Test Author")
    book.description = kwargs.get("description", "Test Description")
    book.status = kwargs.get("status", BookStatus.AVAILABLE)
    book.year = kwargs.get("year", 2024)
    return book


def make_repo() -> tuple[BookRepository, AsyncMock]:
    mock_session = AsyncMock(spec=AsyncSession)
    repo = BookRepository(session=mock_session)
    return repo, mock_session


@pytest.mark.asyncio
async def test_get_all_with_cursor():
    repo, mock_session = make_repo()

    cursor_id = uuid4()
    mock_books = [make_mock_book()]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_books
    mock_session.execute.return_value = mock_result

    result = await repo.get_all(cursor=cursor_id)

    assert len(result) == 1
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_no_cursor():
    repo, mock_session = make_repo()

    mock_books = [make_mock_book(), make_mock_book()]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_books
    mock_session.execute.return_value = mock_result

    result = await repo.get_all()

    assert len(result) == 2
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_found():
    repo, mock_session = make_repo()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_book = make_mock_book(id=fake_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_book
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id(fake_id)

    assert result == mock_book
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found():
    repo, mock_session = make_repo()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id(fake_id)

    assert result is None


@pytest.mark.asyncio
async def test_create_book():
    repo, mock_session = make_repo()

    mock_book = make_mock_book()

    result = await repo.create(mock_book)

    mock_session.add.assert_called_once_with(mock_book)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_book)
    assert result == mock_book


@pytest.mark.asyncio
async def test_delete_by_id_found():
    repo, mock_session = make_repo()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_book = make_mock_book(id=fake_id)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_book
    mock_session.execute.return_value = mock_result

    await repo.delete_by_id(fake_id)

    mock_session.delete.assert_awaited_once_with(mock_book)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id_not_found():
    repo, mock_session = make_repo()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    await repo.delete_by_id(fake_id)

    mock_session.delete.assert_not_awaited()
    mock_session.commit.assert_not_awaited()