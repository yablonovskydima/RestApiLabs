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