from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.core.config import settings

client = AsyncIOMotorClient(settings.DATABASE_MONGO_URL)
db = client[settings.MONGO_DB]

def get_session() -> AsyncIOMotorCollection:
    return db["books"]