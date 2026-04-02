import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.models.book_data import Book
from app.enums.book_status import BookStatus
from app.repository.book_repository import BookRepository


def make_book(**kwargs) -> Book:
    defaults = {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "status": BookStatus.AVAILABLE,
        "description": None,
    }
    return Book(**{**defaults, **kwargs})


def make_mongo_doc(book: Book) -> dict:
    return book.to_mongo()


@pytest.fixture
def collection():
    col = MagicMock()
    col.count_documents = AsyncMock(return_value=0)
    return col


@pytest.fixture
def repo(collection):
    return BookRepository(collection)


@pytest.mark.asyncio
async def test_create_returns_book(repo, collection):
    book = make_book()
    collection.insert_one = AsyncMock(return_value=MagicMock())

    result = await repo.create(book)

    collection.insert_one.assert_called_once_with(book.to_mongo())
    assert result == book


@pytest.mark.asyncio
async def test_get_by_id_returns_book(repo, collection):
    book = make_book()
    collection.find_one = AsyncMock(return_value=make_mongo_doc(book))

    result = await repo.get_by_id(book.id)

    collection.find_one.assert_called_once_with({"_id": str(book.id)})
    assert result.id == book.id
    assert result.title == book.title


@pytest.mark.asyncio
async def test_get_by_id_returns_none(repo, collection):
    collection.find_one = AsyncMock(return_value=None)

    result = await repo.get_by_id(uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_delete_by_id_returns_true(repo, collection):
    book = make_book()
    collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))

    result = await repo.delete_by_id(book.id)

    collection.delete_one.assert_called_once_with({"_id": str(book.id)})
    assert result is True


@pytest.mark.asyncio
async def test_delete_by_id_returns_false_when_not_found(repo, collection):
    collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=0))

    result = await repo.delete_by_id(uuid.uuid4())

    assert result is False


@pytest.mark.asyncio
async def test_get_all_returns_books(repo, collection):
    books = [make_book(title="Dune"), make_book(title="Foundation")]
    docs = [make_mongo_doc(b) for b in books]

    async def async_iter(_):
        for doc in docs:
            yield doc

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__ = async_iter
    collection.find.return_value = cursor
    collection.count_documents = AsyncMock(return_value=2)

    result = await repo.get_all()

    assert result.total == 2
    assert len(result.items) == 2
    assert result.items[0].title == "Dune"
    assert result.items[1].title == "Foundation"


@pytest.mark.asyncio
async def test_get_all_with_status_filter(repo, collection):
    book = make_book(status=BookStatus.AVAILABLE)
    docs = [make_mongo_doc(book)]

    async def async_iter(_):
        for doc in docs:
            yield doc

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__ = async_iter
    collection.find.return_value = cursor
    collection.count_documents = AsyncMock(return_value=1)

    result = await repo.get_all(status=BookStatus.AVAILABLE)

    collection.find.assert_called_once_with({"status": BookStatus.AVAILABLE.value})
    assert result.total == 1
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_get_all_with_sort_by_title(repo, collection):
    async def async_iter(_):
        return
        yield

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__ = async_iter
    collection.find.return_value = cursor
    collection.count_documents = AsyncMock(return_value=0)

    await repo.get_all(sort_by="title")

    cursor.sort.assert_called_once_with("title", 1)