import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4, UUID
from unittest.mock import AsyncMock

from fastapi import FastAPI

from app.api.books import router
from app.dependencies.dependencies import get_book_service
from app.schemas.book import BookStatus, BooksPage, BookResponse
from app.exceptions.exceptions import BookNotFoundError, BookCreateError


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.fixture
def app(mock_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_book_service] = lambda: mock_service
    return app


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def make_book_response(**kwargs) -> dict:
    defaults = {
        "id": uuid4(),
        "title": "Test Book",
        "author": "Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE,
        "year": 2024,
    }
    return {**defaults, **kwargs}


@pytest.mark.asyncio
async def test_get_books_returns_page(client, mock_service):
    book = make_book_response()
    mock_service.get_books = AsyncMock(return_value=BooksPage(
        items=[BookResponse(**book)],
        total=1,
        limit=10,
        offset=0,
    ))

    response = await client.get("/books/?limit=10&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert len(body["items"]) == 1
    mock_service.get_books.assert_awaited_once_with(None, None, None, 10, 0)


@pytest.mark.asyncio
async def test_get_books_with_filters(client, mock_service):
    mock_service.get_books = AsyncMock(return_value=BooksPage(
        items=[], total=0, limit=5, offset=10,
    ))

    response = await client.get(
        "/books/?status_filter=available&author=Shevchenko&sort_by=title&limit=5&offset=10"
    )

    assert response.status_code == 200
    mock_service.get_books.assert_awaited_once_with(
        BookStatus.AVAILABLE, "Shevchenko", "title", 5, 10
    )


@pytest.mark.asyncio
async def test_get_books_invalid_sort_by(client, mock_service):
    response = await client.get("/books/?sort_by=invalid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_book_success(client, mock_service):
    book = make_book_response()
    mock_service.get_book = AsyncMock(return_value=BookResponse(**book))

    response = await client.get(f"/books/{book['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == str(book["id"])
    mock_service.get_book.assert_awaited_once_with(book["id"])


@pytest.mark.asyncio
async def test_get_book_not_found(client, mock_service):
    book_id = uuid4()
    mock_service.get_book = AsyncMock(side_effect=BookNotFoundError)

    response = await client.get(f"/books/{book_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_create_book_success(client, mock_service):
    book_data = {
        "title": "New Book",
        "author": "Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE,
        "year": 2025,
    }
    created = make_book_response(**book_data)
    mock_service.create = AsyncMock(return_value=BookResponse(**created))

    response = await client.post("/books/", json={
        **book_data,
        "status": BookStatus.AVAILABLE.value,
    })

    assert response.status_code == 201
    assert response.json()["title"] == "New Book"
    mock_service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_error(client, mock_service):
    mock_service.create = AsyncMock(side_effect=BookCreateError("Duplicate title"))

    response = await client.post("/books/", json={
        "title": "Some Title",
        "author": "Some Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE.value,
        "year": 2020,
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Duplicate title"


@pytest.mark.asyncio
async def test_delete_book_success(client, mock_service):
    book_id = uuid4()
    mock_service.delete_book = AsyncMock(return_value=None)

    response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 204
    mock_service.delete_book.assert_awaited_once_with(book_id)


@pytest.mark.asyncio
async def test_delete_book_not_found(client, mock_service):
    book_id = uuid4()
    mock_service.delete_book = AsyncMock(side_effect=BookNotFoundError)

    response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"