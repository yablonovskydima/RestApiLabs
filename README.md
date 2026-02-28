# LibraryFastApi

LibraryFastApi is a simple REST API for managing books in a library.
- Built with FastAPI
- Async services using async/await
- Swagger UI for interactive API documentation
- CRUD operations for books

## Usage

1. Clone repository\
``git clone <https://github.com/yablonovskydima/RestApiLabs>``\
``cd LibraryFastApi``


2. Install dependencies using uv\
``uv install``\
``uv add uvicorn``\
``uv add --dev pytest pytest-asyncio``


3. Run application\
``uv run uvicorn app.main:app --reload``


4. Swagger UI is available at:\
``http://127.0.0.1:8000/docs``


## Running Tests
``uv run python -m pytest tests/test_books_api.py``\
Async tests are supported with pytest-asyncio