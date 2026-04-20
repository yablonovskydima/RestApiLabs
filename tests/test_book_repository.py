import pytest
import uuid
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.book_data import Book
from app.enums.book_status import BookStatus
from app.repositories.book_repository import BookRepository


def make_book(**kwargs) -> Book:
    defaults = {
        "id": uuid4(),
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "status": BookStatus.AVAILABLE,
        "description": None,
    }
    return Book(**{**defaults, **kwargs})


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def repo(session):
    return BookRepository(session)


def test_get_all_returns_books(repo, session):
    books = [make_book(title="Dune"), make_book(title="Foundation")]
    session.scalar.return_value = 2
    session.execute.return_value.scalars.return_value.all.return_value = books

    result, total = repo.get_all()

    assert total == 2
    assert len(result) == 2
    assert result[0].title == "Dune"
    assert result[1].title == "Foundation"


def test_get_all_returns_empty_when_no_books(repo, session):
    session.scalar.return_value = 0
    session.execute.return_value.scalars.return_value.all.return_value = []

    result, total = repo.get_all()

    assert total == 0
    assert result == []


def test_get_all_with_status_filter(repo, session):
    book = make_book(status=BookStatus.AVAILABLE)
    session.scalar.return_value = 1
    session.execute.return_value.scalars.return_value.all.return_value = [book]

    result, total = repo.get_all(status=BookStatus.AVAILABLE)

    assert total == 1
    assert result[0].status == BookStatus.AVAILABLE


def test_get_all_with_author_filter(repo, session):
    book = make_book(author="Frank Herbert")
    session.scalar.return_value = 1
    session.execute.return_value.scalars.return_value.all.return_value = [book]

    result, total = repo.get_all(author="Frank")

    assert total == 1
    assert "Herbert" in result[0].author


def test_get_all_with_unknown_author_returns_empty(repo, session):
    session.scalar.return_value = 0
    session.execute.return_value.scalars.return_value.all.return_value = []

    result, total = repo.get_all(author="Nobody")

    assert total == 0
    assert result == []


def test_get_all_sort_by_title(repo, session):
    session.scalar.return_value = 0
    session.execute.return_value.scalars.return_value.all.return_value = []

    repo.get_all(sort_by="title")

    session.execute.assert_called_once()


def test_get_all_sort_by_year(repo, session):
    session.scalar.return_value = 0
    session.execute.return_value.scalars.return_value.all.return_value = []

    repo.get_all(sort_by="year")

    session.execute.assert_called_once()


def test_get_all_unknown_sort_by_is_ignored(repo, session):
    session.scalar.return_value = 0
    session.execute.return_value.scalars.return_value.all.return_value = []

    repo.get_all(sort_by="nonexistent_field")

    session.execute.assert_called_once()


def test_get_all_respects_limit_and_offset(repo, session):
    session.scalar.return_value = 100
    session.execute.return_value.scalars.return_value.all.return_value = []

    repo.get_all(limit=5, offset=20)

    session.execute.assert_called_once()


def test_get_by_id_returns_book(repo, session):
    book = make_book()
    session.get.return_value = book

    result = repo.get_by_id(book.id)

    session.get.assert_called_once_with(Book, book.id)
    assert result.id == book.id
    assert result.title == book.title


def test_get_by_id_returns_none_when_not_found(repo, session):
    session.get.return_value = None

    result = repo.get_by_id(uuid4())

    assert result is None


def test_get_by_id_with_zero_uuid_returns_none(repo, session):
    session.get.return_value = None

    result = repo.get_by_id(uuid.UUID("00000000-0000-0000-0000-000000000000"))

    assert result is None


def test_create_returns_book(repo, session):
    book = make_book()

    result = repo.create(book)

    session.add.assert_called_once_with(book)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(book)
    assert result == book


def test_create_calls_commit(repo, session):
    book = make_book()

    repo.create(book)

    session.commit.assert_called_once()


def test_create_raises_on_session_error(repo, session):
    session.commit.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        repo.create(make_book())


def test_delete_by_id_deletes_existing_book(repo, session):
    book = make_book()
    session.get.return_value = book

    repo.delete_by_id(book.id)

    session.delete.assert_called_once_with(book)
    session.commit.assert_called_once()


def test_delete_by_id_does_nothing_when_not_found(repo, session):
    session.get.return_value = None

    repo.delete_by_id(uuid4())

    session.delete.assert_not_called()
    session.commit.assert_not_called()


def test_delete_by_id_raises_on_session_error(repo, session):
    book = make_book()
    session.get.return_value = book
    session.commit.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        repo.delete_by_id(book.id)


def test_create_book_with_negative_year_raises():
    with pytest.raises(ValueError, match="Year must be non-negative"):
        make_book(year=-1)