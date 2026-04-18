from typing import Optional
from uuid import UUID, uuid4

from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate, BookResponse, BooksPage
from app.enums.book_status import BookStatus
from app.models.book_data import Book
from app.exceptions.exceptions import BookNotFoundError, BookCreateError


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def get_books(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> BooksPage:

        books, total = self.repository.get_all(
            status, author, sort_by, limit, offset
        )

        return BooksPage(
            items=[BookResponse.from_model(b) for b in books],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_book(self, book_id: UUID) -> BookResponse:
        book = self.repository.get_by_id(book_id)

        if not book:
            raise BookNotFoundError(f"Book {book_id} not found")

        return BookResponse.from_model(book)

    def create(self, data: BookCreate) -> BookResponse:
        new_book = Book(
            id=uuid4(),
            title=data.title,
            author=data.author,
            description=data.description,
            status=BookStatus.AVAILABLE,
            year=data.year,
        )

        try:
            book = self.repository.create(new_book)
        except Exception as e:
            raise BookCreateError(str(e))

        return BookResponse.from_model(book)

    def delete_book(self, book_id: UUID) -> None:
        book = self.repository.get_by_id(book_id)

        if not book:
            raise BookNotFoundError(f"Book {book_id} not found")

        self.repository.delete_by_id(book_id)