import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from unittest.mock import AsyncMock

from fastapi import FastAPI

from app.api.books import router
from app.dependencies.dependencies import get_book_service
from app.schemas.book import BookStatus, BookResponse, BooksPage
from app.exceptions.exceptions import BookNotFoundError


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.fixture
def app(mock_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_book_service] = lambda: mock_service  # <-- мокаємо правильну функцію
    return app


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


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
async def test_get_books_returns_page(client, mock_service):
    book = make_book_response()
    mock_service.get_books.return_value = BooksPage(items=[book], next_cursor=None)

    response = await client.get("/books/?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(book.id)
    assert data["next_cursor"] is None
    mock_service.get_books.assert_awaited_once_with(None, None, None, 10, None)


@pytest.mark.asyncio
async def test_get_books_empty(client, mock_service):
    mock_service.get_books.return_value = BooksPage(items=[], next_cursor=None)

    response = await client.get("/books/")

    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_get_books_passes_filters(client, mock_service):
    mock_service.get_books.return_value = BooksPage(items=[], next_cursor=None)

    await client.get("/books/?status_filter=available&author=Shevchenko&sort_by=year&limit=5")

    mock_service.get_books.assert_awaited_once_with(
        BookStatus.AVAILABLE, "Shevchenko", "year", 5, None
    )


@pytest.mark.asyncio
async def test_get_book_success(client, mock_service):
    book = make_book_response()
    mock_service.get_book.return_value = book

    response = await client.get(f"/books/{book.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(book.id)
    mock_service.get_book.assert_awaited_once_with(book.id)


@pytest.mark.asyncio
async def test_get_book_not_found(client, mock_service):
    book_id = uuid4()
    mock_service.get_book.side_effect = BookNotFoundError()

    response = await client.get(f"/books/{book_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_create_book_success(client, mock_service):
    book = make_book_response(title="New Book", year=2025)
    mock_service.create.return_value = book

    payload = {
        "title": "New Book",
        "author": "Test Author",
        "description": "Some description",
        "year": 2025,
    }

    response = await client.post("/books/", json=payload)

    assert response.status_code == 201
    assert response.json()["title"] == "New Book"
    mock_service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_invalid_payload(client, mock_service):
    payload = {"title": "", "author": "AB", "description": "ok", "year": 2025}

    response = await client.post("/books/", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_book_success(client, mock_service):
    book_id = uuid4()
    mock_service.delete_book.return_value = None

    response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 204
    mock_service.delete_book.assert_awaited_once_with(book_id)


@pytest.mark.asyncio
async def test_delete_book_not_found(client, mock_service):
    book_id = uuid4()
    mock_service.delete_book.side_effect = BookNotFoundError()

    response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"