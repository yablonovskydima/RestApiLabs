from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List

from app.models.book_data import Book
from app.enums.book_status import BookStatus


@dataclass
class BookCreate:
    title: str
    author: str
    description: str
    year: int

    def __post_init__(self):
        if not isinstance(self.title, str) or len(self.title.strip()) < 1:
            raise ValueError("Title must be at least 1 character long")

        if not isinstance(self.author, str) or len(self.author.strip()) < 3:
            raise ValueError("Author must be at least 3 characters long")

        if not isinstance(self.description, str) or len(self.description.strip()) < 5:
            raise ValueError("Description must be at least 5 characters long")

        if not isinstance(self.year, int) or self.year < 0:
            raise ValueError("Year must be a non-negative integer")


@dataclass
class BookResponse:
    id: UUID
    title: str
    author: str
    description: Optional[str]
    status: BookStatus
    year: int

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            raise ValueError("id must be a valid UUID")

        if isinstance(self.status, str):
            self.status = BookStatus(self.status)
        elif not isinstance(self.status, BookStatus):
            raise ValueError("Invalid book status")

        if not isinstance(self.year, int) or self.year < 0:
            raise ValueError("Year must be non-negative")

    @classmethod
    def from_model(cls, book: Book) -> "BookResponse":
        return cls(
            id=book.id,
            title=book.title,
            author=book.author,
            description=book.description,
            status=book.status,
            year=book.year,
        )

@dataclass
class BooksPage:
    items: List[BookResponse]
    total: int
    limit: int
    offset: int