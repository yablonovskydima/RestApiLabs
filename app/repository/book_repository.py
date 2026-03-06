from typing import List, Dict, Optional
from uuid import UUID

from app.enums.book_status import BookStatus
from app.models.book_data import Book

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class BookRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        offset: int = 0) -> List[Book]:

        query = select(Book)

        if status:
            query = query.where(Book.status == status)
        if author:
            query = query.where(Book.author.ilike(author))
        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "year":
            query = query.order_by(Book.year)

        query = query.limit(limit).offset(offset)

        books = await self.session.execute(query)
        return list(books.scalars().all())

    async def get_by_id(self, book_id: UUID) -> Book | None:
        result = await self.session.execute(
            select(Book).where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def create(self, book: Book) -> Book:
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)
        return book

    async def delete_by_id(self, book_id: UUID) -> None:
        book = await self.get_by_id(book_id)
        if book:
            await self.session.delete(book)
            await self.session.commit()