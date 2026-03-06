from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RETIRED = "retired"