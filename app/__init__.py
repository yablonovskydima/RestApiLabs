from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def health():
        return {"status": "ok"}

    return app