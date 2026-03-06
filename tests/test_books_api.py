import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from unittest.mock import AsyncMock

from fastapi import FastAPI

from app.api.books import router, get_book_service
from app.schemas.book import BookStatus


@pytest.fixture
def mock_service():
    service = AsyncMock()
    return service


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


@pytest.mark.asyncio
async def test_get_books(client, mock_service):
    mock_service.get_books = AsyncMock(return_value=[
        {
            "id": str(uuid4()),
            "title": "Test Book",
            "author": "Author",
            "description": "Some description",
            "status": BookStatus.AVAILABLE,
            "year": 2024,
        }
    ])

    response = await client.get("/books/?limit=10&offset=0")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_books.assert_awaited_once_with(None, None, None, 10, 0)


@pytest.mark.asyncio
async def test_get_book_success(client, mock_service):
    book_id = uuid4()

    mock_service.get_book = AsyncMock(return_value={
        "id": str(book_id),
        "title": "Test",
        "author": "Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE,
        "year": 2023
    })

    response = await client.get(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(book_id)
    mock_service.get_book.assert_awaited_once_with(book_id)


@pytest.mark.asyncio
async def test_get_book_not_found(client, mock_service):
    book_id = uuid4()

    mock_service.get_book = AsyncMock(return_value=None)

    response = await client.get(f"/books/{book_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_create_book(client, mock_service):
    book_data = {
        "title": "New Book",
        "author": "Author",
        "description": "Some description",
        "status": BookStatus.AVAILABLE,
        "year": 2025
    }

    created_book = {"id": str(uuid4()), **book_data}
    mock_service.create = AsyncMock(return_value=created_book)

    response = await client.post("/books/", json=book_data)

    assert response.status_code == 201
    assert response.json()["title"] == "New Book"
    mock_service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_book_success(client, mock_service):
    book_id = uuid4()

    mock_service.get_book = AsyncMock(return_value={"id": str(book_id)})
    mock_service.delete_book = AsyncMock(return_value=None)

    response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 204
    mock_service.delete_book.assert_awaited_once_with(book_id)


@pytest.mark.asyncio
async def test_delete_book_not_found(client, mock_service):
    book_id = uuid4()

    mock_service.get_book = AsyncMock(return_value=None)

    response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"