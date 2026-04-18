from flask import Blueprint, request, jsonify, g
from uuid import UUID

from app.services.book_service import BookService
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate, BookResponse
from app.enums.book_status import BookStatus
from app.exceptions.exceptions import BookNotFoundError, BookCreateError

book_bp = Blueprint("books", __name__)


def get_service():
    return BookService(BookRepository(g.db))


def serialize_book(book: BookResponse) -> dict:
    return {
        "id": str(book.id),
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "status": book.status.value,
        "year": book.year,
    }


@book_bp.route("/", methods=["GET"])
def get_books():
    """
    Get list of books
    ---
    parameters:
      - name: status
        in: query
        type: string
        enum: [AVAILABLE, BORROWED]
        required: false
      - name: author
        in: query
        type: string
        required: false
      - name: sort_by
        in: query
        type: string
        required: false
      - name: limit
        in: query
        type: integer
        default: 10
      - name: offset
        in: query
        type: integer
        default: 0
    responses:
      200:
        description: List of books
    """
    service = get_service()

    try:
        status = request.args.get("status")
        author = request.args.get("author")
        sort_by = request.args.get("sort_by")
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        status_enum = BookStatus(status) if status else None

        result = service.get_books(
            status=status_enum,
            author=author,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )

        return jsonify({
            "total": result.total,
            "limit": result.limit,
            "offset": result.offset,
            "items": [serialize_book(item) for item in result.items]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@book_bp.route("/<uuid:book_id>", methods=["GET"])
def get_book(book_id: UUID):
    """
    Get book by ID
    ---
    parameters:
      - name: book_id
        in: path
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Book found
      404:
        description: Book not found
    """
    service = get_service()

    try:
        book = service.get_book(book_id)
        return jsonify(serialize_book(book))

    except BookNotFoundError:
        return jsonify({"error": "Book not found"}), 404


@book_bp.route("/", methods=["POST"])
def create_book():
    """
    Create a new book
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - author
          properties:
            title:
              type: string
              example: "The Great Gatsby"
            author:
              type: string
              example: "F. Scott Fitzgerald"
            description:
              type: string
              example: "A story about the American dream"
            year:
              type: integer
              example: 1925
    responses:
      201:
        description: Book created
      400:
        description: Validation error
    """
    service = get_service()

    try:
        data = request.json
        book_data = BookCreate(**data)
        book = service.create(book_data)

        return jsonify(serialize_book(book)), 201

    except BookCreateError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@book_bp.route("/<uuid:book_id>", methods=["DELETE"])
def delete_book(book_id: UUID):
    """
    Delete book
    ---
    parameters:
      - name: book_id
        in: path
        type: string
        format: uuid
        required: true
    responses:
      204:
        description: Book deleted
      404:
        description: Book not found
    """
    service = get_service()

    try:
        service.delete_book(book_id)
        return "", 204

    except BookNotFoundError:
        return jsonify({"error": "Book not found"}), 404