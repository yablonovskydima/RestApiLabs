from fastapi import HTTPException

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.schemas.book import BookStatus, BookResponse, BooksPage
from app.exceptions.exceptions import BookNotFoundError
from app.api.books import get_books, get_book, create_book, delete_book
from app.schemas.book import BookCreate  # adjust if needed


@pytest.fixture
def mock_service():
    return AsyncMock()


def make_book_response(**kwargs) -> BookResponse:
    defaults = {
        "id": uuid4(),
        "title": "Test Book",
        "author": "Test Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE,
        "year": 2024,
    }
    return BookResponse(**{**defaults, **kwargs})


@pytest.mark.asyncio
async def test_get_books_returns_page(mock_service):
    book = make_book_response()
    mock_service.get_books.return_value = BooksPage(items=[book], next_cursor=None)

    result = await get_books(
        status_filter=None, author=None, sort_by=None, limit=10, cursor=None,
        service=mock_service,
    )

    assert len(result.items) == 1
    assert result.items[0].id == book.id
    mock_service.get_books.assert_awaited_once_with(None, None, None, 10, None)


@pytest.mark.asyncio
async def test_get_books_empty(mock_service):
    mock_service.get_books.return_value = BooksPage(items=[], next_cursor=None)

    result = await get_books(
        status_filter=None, author=None, sort_by=None, limit=10, cursor=None,
        service=mock_service,
    )

    assert result.items == []


@pytest.mark.asyncio
async def test_get_books_passes_filters(mock_service):
    mock_service.get_books.return_value = BooksPage(items=[], next_cursor=None)

    await get_books(
        status_filter=BookStatus.AVAILABLE, author="Shevchenko", sort_by="year", limit=5, cursor=None,
        service=mock_service,
    )

    mock_service.get_books.assert_awaited_once_with(BookStatus.AVAILABLE, "Shevchenko", "year", 5, None)


@pytest.mark.asyncio
async def test_get_book_success(mock_service):
    book = make_book_response()
    mock_service.get_book.return_value = book

    result = await get_book(book_id=book.id, service=mock_service)

    assert result.id == book.id
    mock_service.get_book.assert_awaited_once_with(book.id)


@pytest.mark.asyncio
async def test_get_book_not_found(mock_service):
    mock_service.get_book.side_effect = BookNotFoundError()

    try:
        await get_book(book_id=uuid4(), service=mock_service)
        pytest.fail("Expected HTTPException was not raised")
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == "Book not found"


@pytest.mark.asyncio
async def test_create_book_success(mock_service):
    book = make_book_response(title="New Book", year=2025)
    mock_service.create.return_value = book

    payload = BookCreate(
        title="New Book",
        author="Test Author",
        description="Some description",
        year=2025,
    )

    result = await create_book(book=payload, service=mock_service)
    assert result.title == "New Book"
    mock_service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_book_success(mock_service):
    book_id = uuid4()
    mock_service.delete_book.return_value = None

    await delete_book(book_id=book_id, service=mock_service)

    mock_service.delete_book.assert_awaited_once_with(book_id)


@pytest.mark.asyncio
async def test_delete_book_not_found(mock_service):
    mock_service.delete_book.side_effect = BookNotFoundError()

    try:
        await delete_book(book_id=uuid4(), service=mock_service)
        pytest.fail("Expected HTTPException was not raised")
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == "Book not found"