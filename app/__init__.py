from flask import Flask, g
from flasgger import Swagger

from app.db.database import SessionLocal, engine
from app.models.book_data import Base
from app.api.books import book_bp


def create_app():
    app = Flask(__name__)

    swagger = Swagger(app, template={
        "info": {
            "title": "Books API",
            "description": "API for managing books",
            "version": "1.0.0"
        },
        "definitions": {
            "BookResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid", "example": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
                    "title": {"type": "string", "example": "The Great Gatsby"},
                    "author": {"type": "string", "example": "F. Scott Fitzgerald"},
                    "description": {"type": "string", "nullable": True, "example": "A story about the American dream"},
                    "status": {"type": "string", "enum": ["AVAILABLE", "BORROWED"], "example": "AVAILABLE"},
                    "year": {"type": "integer", "example": 1925}
                }
            },
            "BookCreate": {
                "type": "object",
                "required": ["title", "author", "description", "year"],
                "properties": {
                    "title": {"type": "string", "minLength": 1, "example": "The Great Gatsby"},
                    "author": {"type": "string", "minLength": 3, "example": "F. Scott Fitzgerald"},
                    "description": {"type": "string", "minLength": 5, "example": "A story about the American dream"},
                    "year": {"type": "integer", "minimum": 0, "example": 1925}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Book not found"}
                }
            },
            "ErrorCreateResponse" : {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Could not create a book"}
                }
            }
        }
    })

    @app.before_request
    def create_session():
        g.db = SessionLocal()

    @app.teardown_request
    def shutdown_session(exception=None):
        db = g.pop("db", None)
        if db:
            db.close()

    Base.metadata.create_all(bind=engine)

    app.register_blueprint(book_bp, url_prefix="/books")

    return app