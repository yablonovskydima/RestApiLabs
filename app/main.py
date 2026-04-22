from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.books import router as books_router
from app.api.auth import router as auth_router
from app.db.session import engine
from app.models.book_data import Base
import app.models.users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Library API",
    description="Library API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(books_router, tags=["Books"])