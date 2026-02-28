from fastapi import FastAPI
from app.api.books import router as books_router

app = FastAPI(
    title="Library API",
    description="Library API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(books_router, prefix="/books", tags=["Books"])