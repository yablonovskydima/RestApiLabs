from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorCollection

from app.enums.book_status import BookStatus
from app.models.book_data import Book


class BookRepository:

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_all(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Book]:

        filters = {}

        if status:
            filters["status"] = status.value
        if author:
            filters["author"] = {"$regex": author, "$options": "i"}

        cursor = self.collection.find(filters)

        if sort_by == "title":
            cursor = cursor.sort("title", 1)
        elif sort_by == "year":
            cursor = cursor.sort("year", 1)

        cursor = cursor.skip(offset).limit(limit)

        books = []
        async for document in cursor:
            books.append(Book.from_mongo(document))

        return books

    async def get_by_id(self, book_id: UUID) -> Book | None:
        document = await self.collection.find_one({"_id": str(book_id)})
        if document is None:
            return None
        return Book.from_mongo(document)

    async def create(self, book: Book) -> Book:
        await self.collection.insert_one(book.to_mongo())
        return book

    async def delete_by_id(self, book_id: UUID) -> bool:
        response = await self.collection.delete_one({"_id": str(book_id)})
        return response.deleted_count > 0