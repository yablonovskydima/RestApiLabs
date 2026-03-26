from typing import Optional
from uuid import UUID, uuid4

from app.repository.book_repository import BookRepository
from app.schemas.book import BookCreate, BookResponse, BooksPage
from app.enums.book_status import BookStatus
from app.models.book_data import Book
from app.exceptions.exceptions import BookNotFoundError, BookCreateError


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def get_books(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[UUID] = None,
    ) -> BooksPage:
        books = await self.repository.get_all(status, author, sort_by, limit + 1, cursor)

        has_next = len(books) > limit
        books = books[:limit]

        next_cursor = books[-1].id if has_next and books else None

        return BooksPage(
            items=[BookResponse.from_model(b) for b in books],
            next_cursor=next_cursor,
        )

    async def get_book(self, book_id: UUID) -> BookResponse:
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book {book_id} not found")
        return BookResponse.from_model(book)

    async def create(self, data: BookCreate) -> BookResponse:
        new_book = Book(
            id=uuid4(),
            title=data.title,
            author=data.author,
            description=data.description,
            status=BookStatus.AVAILABLE,
            year=data.year,
        )
        try:
            book = await self.repository.create(new_book)
        except Exception as e:
            raise BookCreateError(str(e))
        return BookResponse.from_model(book)

    async def delete_book(self, book_id: UUID) -> None:
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book {book_id} not found")
        await self.repository.delete_by_id(book_id)