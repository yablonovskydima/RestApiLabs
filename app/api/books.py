from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status, HTTPException

from app.schemas.book import BookStatus, BookResponse, BookCreate, BooksPage
from app.dependencies.dependencies import BookServiceDep

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=BooksPage)
async def get_books(
    service: BookServiceDep,
    status_filter: Optional[BookStatus] = Query(None),
    author: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$"),
    limit: int = Query(10, ge=1, le=100),
    cursor: Optional[UUID] = Query(None),
):
    return await service.get_books(status_filter, author, sort_by, limit, cursor)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: UUID, service: BookServiceDep):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, service: BookServiceDep):
    try:
        return await service.create(book)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create book")


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, service: BookServiceDep):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await service.delete_book(book_id)