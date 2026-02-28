from typing import List, Dict, Optional
from uuid import UUID

from app.schemas.book import BookStatus
from app.models.book_data import book_data


class BookRepository:

    async def get_all(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> List[Dict]:

        books = book_data

        if status:
            books = [b for b in books if b["status"] == status]

        if author:
            books = [
                b for b in books
                if b["author"].lower() == author.lower()
            ]

        if sort_by == "title":
            books = sorted(books, key=lambda x: x["title"])
        elif sort_by == "year":
            books = sorted(books, key=lambda x: x["year"])

        return books

    async def get_by_id(self, book_id: UUID) -> dict | None:
        for book in book_data:
            if book['id'] == book_id:
                return book
        return None

    async def create(self, book: Dict) -> None:
        book_data.append(book)

    async def delete_by_id(self, book_id: UUID) -> None:
        global book_data
        book_data[:] = [
            book for book in book_data if book["id"] != book_id
        ]