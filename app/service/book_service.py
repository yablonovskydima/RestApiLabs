from typing import Optional, List
from uuid import UUID, uuid4

from app.repository.book_repository import BookRepository
from app.schemas.book import BookCreate, BookResponse, BooksPage

from app.enums.book_status import BookStatus
from app.models.book_data import Book

class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def get_books(self,
                        status: Optional[BookStatus] = None,
                        author: Optional[str] = None,
                        sort_by: Optional[str] = None,
                        limit: int = 10,
                        cursor: Optional[UUID] = None) -> BooksPage:
        books = await self.repository.get_all(status, author, sort_by, limit, cursor)
        next_cursor = books[-1].id if len(books) == limit else None
        return BooksPage(
            items=[BookResponse.from_model(b) for b in books],
            next_cursor=next_cursor,
        )

    async def get_book(self, book_id: UUID) -> BookResponse | None:
        book = await self.repository.get_by_id(book_id)
        if not book:
            return None
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

        book = await self.repository.create(new_book)
        return BookResponse.from_model(book)

    async def delete_book(self, book_id: UUID) -> None:
        await self.repository.delete_by_id(book_id)