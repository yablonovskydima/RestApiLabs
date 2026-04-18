from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.book_data import Book
from app.enums.book_status import BookStatus


class BookRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ):
        filters = []

        if status:
            filters.append(Book.status == status)
        if author:
            filters.append(Book.author.ilike(f"%{author}%"))

        total = self.session.scalar(
            select(func.count()).select_from(Book).where(*filters)
        )

        query = select(Book).where(*filters)

        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "year":
            query = query.order_by(Book.year)

        query = query.limit(limit).offset(offset)

        result = self.session.execute(query)
        return result.scalars().all(), total

    def get_by_id(self, book_id: UUID) -> Book | None:
        return self.session.get(Book, book_id)

    def create(self, book: Book) -> Book:
        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def delete_by_id(self, book_id: UUID):
        book = self.get_by_id(book_id)
        if book:
            self.session.delete(book)
            self.session.commit()