import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.schemas.book import BookStatus, BooksPage, BookResponse
from app.exceptions.exceptions import BookNotFoundError, BookCreateError
from app.service.book_service import BookService


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return BookService(mock_repo)


def make_book_response(**kwargs) -> BookResponse:
    defaults = {
        "id": uuid4(),
        "title": "Test Book",
        "author": "Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE,
        "year": 2024,
    }
    return BookResponse(**{**defaults, **kwargs})


@pytest.mark.asyncio
async def test_get_books_returns_page(service, mock_repo):
    book = make_book_response()
    mock_repo.get_all = AsyncMock(return_value=BooksPage(
        items=[book], total=1, limit=10, offset=0,
    ))

    result = await service.get_books(None, None, None, 10, 0)

    assert result.total == 1
    assert result.limit == 10
    assert result.offset == 0
    assert len(result.items) == 1
    mock_repo.get_all.assert_awaited_once_with(None, None, None, 10, 0)


@pytest.mark.asyncio
async def test_get_books_with_filters(service, mock_repo):
    mock_repo.get_all = AsyncMock(return_value=BooksPage(
        items=[], total=0, limit=5, offset=10,
    ))

    result = await service.get_books(BookStatus.AVAILABLE, "Shevchenko", "title", 5, 10)

    assert result.total == 0
    mock_repo.get_all.assert_awaited_once_with(BookStatus.AVAILABLE, "Shevchenko", "title", 5, 10)


@pytest.mark.asyncio
async def test_get_book_success(service, mock_repo):
    book = make_book_response()
    mock_repo.get_by_id = AsyncMock(return_value=book)

    result = await service.get_book(book.id)

    assert result.id == book.id
    mock_repo.get_by_id.assert_awaited_once_with(book.id)


@pytest.mark.asyncio
async def test_get_book_not_found(service, mock_repo):
    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(BookNotFoundError):
        await service.get_book(uuid4())


@pytest.mark.asyncio
async def test_create_book_success(service, mock_repo):
    book = make_book_response(title="New Book")
    mock_repo.create = AsyncMock(return_value=book)

    result = await service.create(book)

    assert result.title == "New Book"
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_error(service, mock_repo):
    mock_repo.create = AsyncMock(side_effect=BookCreateError("Duplicate title"))

    with pytest.raises(BookCreateError) as exc_info:
        await service.create(make_book_response())

    assert str(exc_info.value) == "Duplicate title"


@pytest.mark.asyncio
async def test_delete_book_success(service, mock_repo):
    book_id = uuid4()
    book = make_book_response(id=book_id)
    mock_repo.get_by_id = AsyncMock(return_value=book)
    mock_repo.delete_by_id = AsyncMock(return_value=True)

    await service.delete_book(book_id)

    mock_repo.delete_by_id.assert_awaited_once_with(book_id)


@pytest.mark.asyncio
async def test_delete_book_not_found(service, mock_repo):
    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(BookNotFoundError):
        await service.delete_book(uuid4())