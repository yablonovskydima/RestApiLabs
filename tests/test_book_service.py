import pytest
from uuid import UUID, uuid4
from unittest.mock import MagicMock

from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookResponse, BooksPage
from app.enums.book_status import BookStatus
from app.models.book_data import Book
from app.exceptions.exceptions import BookNotFoundError, BookCreateError


def make_mock_book(**kwargs) -> MagicMock:
    book = MagicMock(spec=Book)
    book.id = kwargs.get("id", uuid4())
    book.title = kwargs.get("title", "Test Book")
    book.author = kwargs.get("author", "Test Author")
    book.description = kwargs.get("description", "Test Description")
    book.status = kwargs.get("status", BookStatus.AVAILABLE)
    book.year = kwargs.get("year", 2024)
    return book


def make_book_create(**kwargs) -> BookCreate:
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "year": 2024,
    }
    return BookCreate(**{**defaults, **kwargs})


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return BookService(repository=mock_repo)



def test_get_books_returns_page(service, mock_repo):
    books = [make_mock_book(title="Book1"), make_mock_book(title="Book2")]
    mock_repo.get_all.return_value = (books, 2)

    result = service.get_books()

    assert isinstance(result, BooksPage)
    assert result.total == 2
    assert result.limit == 10
    assert result.offset == 0
    assert len(result.items) == 2
    mock_repo.get_all.assert_called_once_with(None, None, None, 10, 0)


def test_get_books_with_filters(service, mock_repo):
    books = [make_mock_book(title="Book1"), make_mock_book(title="Book2")]
    mock_repo.get_all.return_value = (books, 2)

    result = service.get_books(
        status=BookStatus.AVAILABLE,
        author="Author",
        sort_by="title",
        limit=10,
        offset=0,
    )

    assert result.total == 2
    assert len(result.items) == 2
    mock_repo.get_all.assert_called_once_with(BookStatus.AVAILABLE, "Author", "title", 10, 0)


def test_get_books_returns_empty_when_no_books(service, mock_repo):
    mock_repo.get_all.return_value = ([], 0)

    result = service.get_books()

    assert result.total == 0
    assert result.items == []


def test_get_books_items_are_book_response(service, mock_repo):
    mock_repo.get_all.return_value = ([make_mock_book()], 1)

    result = service.get_books()

    assert all(isinstance(item, BookResponse) for item in result.items)


def test_get_books_respects_limit_and_offset(service, mock_repo):
    mock_repo.get_all.return_value = ([], 0)

    result = service.get_books(limit=5, offset=20)

    assert result.limit == 5
    assert result.offset == 20
    mock_repo.get_all.assert_called_once_with(None, None, None, 5, 20)


def test_get_book_returns_book_response(service, mock_repo):
    fake_id = UUID("11111111-1111-1111-1111-111111111111")
    mock_book = make_mock_book(id=fake_id)
    mock_repo.get_by_id.return_value = mock_book

    result = service.get_book(fake_id)

    assert isinstance(result, BookResponse)
    assert result.id == fake_id
    mock_repo.get_by_id.assert_called_once_with(fake_id)


def test_get_book_not_found_raises(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundError):
        service.get_book(uuid4())


def test_get_book_not_found_message_contains_id(service, mock_repo):
    fake_id = UUID("22222222-2222-2222-2222-222222222222")
    mock_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundError, match=str(fake_id)):
        service.get_book(fake_id)


def test_create_returns_book_response(service, mock_repo):
    data = make_book_create()
    mock_repo.create.return_value = make_mock_book(title=data.title, author=data.author)

    result = service.create(data)

    assert isinstance(result, BookResponse)
    assert result.title == data.title
    assert result.author == data.author
    mock_repo.create.assert_called_once()


def test_create_sets_status_available(service, mock_repo):
    mock_repo.create.return_value = make_mock_book(status=BookStatus.AVAILABLE)

    result = service.create(make_book_create())

    assert result.status == BookStatus.AVAILABLE


def test_create_generates_new_uuid(service, mock_repo):
    mock_repo.create.return_value = make_mock_book()

    result = service.create(make_book_create())

    assert isinstance(result.id, UUID)


def test_create_raises_book_create_error_on_repo_failure(service, mock_repo):
    mock_repo.create.side_effect = Exception("DB constraint violated")

    with pytest.raises(BookCreateError, match="DB constraint violated"):
        service.create(make_book_create())


def test_create_wraps_any_exception_in_book_create_error(service, mock_repo):
    mock_repo.create.side_effect = RuntimeError("unexpected")

    with pytest.raises(BookCreateError):
        service.create(make_book_create())


def test_delete_book_calls_delete_by_id(service, mock_repo):
    fake_id = UUID("33333333-3333-3333-3333-333333333333")
    mock_repo.get_by_id.return_value = make_mock_book(id=fake_id)

    service.delete_book(fake_id)

    mock_repo.delete_by_id.assert_called_once_with(fake_id)


def test_delete_book_checks_existence_first(service, mock_repo):
    fake_id = uuid4()
    mock_repo.get_by_id.return_value = make_mock_book(id=fake_id)

    service.delete_book(fake_id)

    mock_repo.get_by_id.assert_called_once_with(fake_id)


def test_delete_book_not_found_raises(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundError):
        service.delete_book(uuid4())


def test_delete_book_not_found_does_not_call_delete(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundError):
        service.delete_book(uuid4())

    mock_repo.delete_by_id.assert_not_called()
