from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.books import router as books_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(books_router, tags=["Books"])