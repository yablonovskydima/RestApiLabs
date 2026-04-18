import uuid
from typing import Optional

from sqlalchemy import String, Integer, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

from app.enums.book_status import BookStatus


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[BookStatus] = mapped_column(
        SAEnum(BookStatus, name="book_status"),
        default=BookStatus.AVAILABLE,
        nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    @validates("year")
    def validate_year(self, key, value):
        if value < 0:
            raise ValueError("Year must be non-negative")
        return value

    def __repr__(self):
        return f"<Book {self.title}>"