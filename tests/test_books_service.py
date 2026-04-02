import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock

from app.service.book_service import BookService
from app.schemas.book import BookCreate, BookResponse, BooksPage
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


def make_service() -> tuple[BookService, AsyncMock]:
    mock_repo = AsyncMock()
    service = BookService(repository=mock_repo)
    return service, mock_repo


@pytest.mark.asyncio
async def test_create_book_success():
    service, mock_repo = make_service()

    data = BookCreate(
        title="Test Book",
        author="Test Author",
        description="Test Description",
        year=2024,
    )

    mock_book = make_mock_book(title="Test Book", author="Test Author")
    mock_repo.create.return_value = mock_book

    result = await service.create(data)

    assert isinstance(result, BookResponse)
    assert result.title == "Test Book"
    assert result.author == "Test Author"
    assert result.status == BookStatus.AVAILABLE
    assert isinstance(result.id, UUID)
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_books_with_filters():
    service, mock_repo = make_service()

    mock_books = [make_mock_book(title="Book1"), make_mock_book(title="Book2")]
    mock_repo.get_all.return_value = BooksPage(
        items=mock_books,
        total=2,
        limit=10,
        offset=0,
    )

    result = await service.get_books(
        status=BookStatus.AVAILABLE,
        author="Author",
        sort_by="title",
        limit=10,
        offset=0,
    )

    assert result.total == 2
    assert len(result.items) == 2
    mock_repo.get_all.assert_awaited_once_with(
        BookStatus.AVAILABLE, "Author", "title", 10, 0
    )


@pytest.mark.asyncio
async def test_get_book_by_id():
    service, mock_repo = make_service()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_book = make_mock_book(id=fake_id)
    mock_repo.get_by_id.return_value = mock_book

    result = await service.get_book(fake_id)

    assert isinstance(result, BookResponse)
    assert result.id == fake_id
    mock_repo.get_by_id.assert_awaited_once_with(fake_id)


@pytest.mark.asyncio
async def test_get_book_not_found():
    from app.exceptions.exceptions import BookNotFoundError

    service, mock_repo = make_service()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundError):
        await service.get_book(fake_id)

    mock_repo.get_by_id.assert_awaited_once_with(fake_id)


@pytest.mark.asyncio
async def test_delete_book():
    service, mock_repo = make_service()

    fake_id = UUID("11111111-1111-1111-1111-111111111111")

    await service.delete_book(fake_id)

    mock_repo.delete_by_id.assert_awaited_once_with(fake_id)