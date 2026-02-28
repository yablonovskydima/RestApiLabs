from typing import Optional, List
from uuid import UUID, uuid4

from app.repository.book_repository import BookRepository
from app.schemas.book import BookStatus, BookCreate


class BookService:
    def __init__(self):
        self.repository = BookRepository()

    async def get_books(self,
                        status: Optional[BookStatus] = None,
                        author: Optional[str] = None,
                        sort_by: Optional[str] = None,) -> List[dict]:

        return await self.repository.get_all(status, author, sort_by)

    async def get_book(self, book_id: UUID) -> dict:
        return await self.repository.get_by_id(book_id)

    async def create(self, data: BookCreate) -> dict:
        new_book = {
            "id": uuid4(),
            "title": data.title,
            "author": data.author,
            "description": data.description,
            "status": BookStatus.AVAILABLE,
            "year": data.year,
        }

        await self.repository.create(new_book)
        return new_book

    async def delete_book(self, book_id: UUID) -> None:
        await self.repository.delete_by_id(book_id)