from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.session import get_session
from app.repository.book_repository import BookRepository
from app.service.book_service import BookService


def get_book_service(collection: AsyncIOMotorCollection = Depends(get_session)) -> BookService:
    repository = BookRepository(collection)
    return BookService(repository)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]