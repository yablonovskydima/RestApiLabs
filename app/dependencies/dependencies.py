from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.session import get_session
from app.repository.book_repository import BookRepository
from app.service.book_service import BookService


def get_book_service(session: AsyncSession = Depends(get_session)) -> BookService:
    repository = BookRepository(session)
    return BookService(repository)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]