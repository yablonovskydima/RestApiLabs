import pytest
from uuid import UUID
from unittest.mock import AsyncMock

from app.service.book_service import BookService
from app.schemas.book import BookCreate, BookStatus


@pytest.mark.asyncio
async def test_create_book_success():
    service = BookService()

    mock_repo = AsyncMock()
    service.repository = mock_repo

    data = BookCreate(
        title="Test Book",
        author="Test Author",
        description="Test Description",
        year=2024,
    )

    result = await service.create(data)

    assert result["title"] == "Test Book"
    assert result["author"] == "Test Author"
    assert result["status"] == BookStatus.AVAILABLE
    assert isinstance(result["id"], UUID)

    mock_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_books_with_filters():
    service = BookService()
    mock_repo = AsyncMock()
    service.repository = mock_repo

    mock_repo.get_all.return_value = [{"title": "Book1"}]

    result = await service.get_books(
        status=BookStatus.AVAILABLE,
        author="Author",
        sort_by="title",
    )

    assert result == [{"title": "Book1"}]

    mock_repo.get_all.assert_awaited_once_with(
        BookStatus.AVAILABLE,
        "Author",
        "title",
    )

@pytest.mark.asyncio
async def test_get_book_by_id():
    service = BookService()
    mock_repo = AsyncMock()
    service.repository = mock_repo

    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_repo.get_by_id.return_value = {"id": fake_id}

    result = await service.get_book(fake_id)

    assert result["id"] == fake_id
    mock_repo.get_by_id.assert_awaited_once_with(fake_id)

@pytest.mark.asyncio
async def test_delete_book():
    service = BookService()
    mock_repo = AsyncMock()
    service.repository = mock_repo

    fake_id = UUID("11111111-1111-1111-1111-111111111111")

    await service.delete_book(fake_id)

    mock_repo.delete_by_id.assert_awaited_once_with(fake_id)