import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.enums.book_status import BookStatus


class Book(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    author: str
    description: Optional[str] = None
    status: BookStatus = BookStatus.AVAILABLE
    year: int

    model_config = {
        "use_enum_values": True,
        "populate_by_name": True,
    }

    def to_mongo(self) -> dict:
        data = self.model_dump()
        data["_id"] = str(data.pop("id"))
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "Book":
        data["id"] = data.pop("_id")
        return cls(**data)