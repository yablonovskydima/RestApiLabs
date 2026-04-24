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
        enum: [AVAILABLE, BORROWED, RETIRED]
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
        description: Paginated list of books
        schema:
          type: object
          properties:
            total:
              type: integer
              example: 42
            limit:
              type: integer
              example: 10
            offset:
              type: integer
              example: 0
            items:
              type: array
              items:
                $ref: '#/definitions/BookResponse'
      404:
        description: Invalid query parameters
        schema:
          $ref: '#/definitions/ErrorResponse'
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
        return jsonify({"error": str(e)}), 404


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
        example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    responses:
      200:
        description: Book found
        schema:
          $ref: '#/definitions/BookResponse'
      404:
        description: Book not found
        schema:
          $ref: '#/definitions/ErrorResponse'
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
          $ref: '#/definitions/BookCreate'
    responses:
      201:
        description: Book created successfully
        schema:
          $ref: '#/definitions/BookResponse'
      400:
        description: Validation error or invalid input
        schema:
          $ref: '#/definitions/ErrorCreateResponse'
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
        example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    responses:
      204:
        description: Book deleted successfully
      404:
        description: Book not found
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    service = get_service()

    try:
        service.delete_book(book_id)
        return "", 204

    except BookNotFoundError:
        return jsonify({"error": "Book not found"}), 404


definitions = """
definitions:
  BookResponse:
    type: object
    properties:
      id:
        type: string
        format: uuid
        example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
      title:
        type: string
        example: "The Great Gatsby"
      author:
        type: string
        example: "F. Scott Fitzgerald"
      description:
        type: string
        nullable: true
        example: "A story about the American dream"
      status:
        type: string
        enum: [AVAILABLE, BORROWED, RETIRED]
        example: "AVAILABLE"
      year:
        type: integer
        example: 1925

  BookCreate:
    type: object
    required:
      - title
      - author
      - description
      - year
    properties:
      title:
        type: string
        minLength: 1
        example: "The Great Gatsby"
      author:
        type: string
        minLength: 3
        example: "F. Scott Fitzgerald"
      description:
        type: string
        minLength: 5
        example: "A story about the American dream"
      year:
        type: integer
        minimum: 0
        example: 1925

  ErrorResponse:
    type: object
    properties:
      error:
        type: string
        example: "Book not found"
        
 
  ErrorCreateResponse:
    type: object
    properties:
      error:
        type: string
        example: "Could not create a book"
"""