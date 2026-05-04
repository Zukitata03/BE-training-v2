import uuid
import time
from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi, validate

from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
from app.databases.redis_cached import RedisCache
from app.decorators.auth import protected
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError, ApiNotFound, ApiForbidden
from app.models.book import create_book_json_schema, Book

books_bp = Blueprint('books_blueprint', url_prefix='/books')

_db = MongoDB()


@books_bp.get('/')
# Config swagger example
@openapi.tag('Books')
@openapi.summary('Get all books')
@openapi.description('Get all books from database')
# -----
async def get_all_books(request):
    # # TODO: use cache to optimize api
    cache: RedisCache = request.app.ctx.cache
    books = await cache.get(CacheConstants.all_books)
    if books is None:
        book_objs = _db.get_books()
        books = [book.to_dict() for book in book_objs]
        await cache.set(CacheConstants.all_books, books)
    return json({'data': {
        'n_books': len(books),
        'books': books
    }})


@books_bp.post('/')
# Config swagger example
@openapi.tag('Books')
@openapi.summary('Create a book')
@openapi.description('Create a book in database')
@openapi.body({'application/json': create_book_json_schema})
# -----
# Validate body before auth so bad JSON yields 400, not 401
@validate_with_jsonschema(jsonschema=create_book_json_schema)
@protected
async def create_book(request, username: str):
    body = request.json

    book_id = str(uuid.uuid4())
    book = Book(book_id).from_dict(body)
    book.owner = username

    # # TODO: Save book to database
    inserted = _db.add_book(book)
    if not inserted:
        raise ApiInternalError('Fail to create book')

    # TODO: Update cache
    await request.app.ctx.cache.delete(CacheConstants.all_books)
    return json({'data': {
        'message': 'created',
        'book': book.to_dict()
    }}, status=201)



# TODO: write api get, update, delete book

# GET /books/{id}
@books_bp.get('/<book_id:str>')
@openapi.tag('Books')
@openapi.summary('Get a book by id')
@openapi.description('Get a book by id from database')

# -----
async def get_book_by_id(request, book_id: str):
    book = _db.get_book_by_id(book_id)
    if not book:
        raise ApiNotFound(f'Book with id {book_id} not found')
    return json({'data': {
        'book': book.to_dict()
    }})

# PUT /books/{id}
@books_bp.put('/<book_id:str>')
@openapi.tag('Books')
@openapi.summary('Update a book by id')
@openapi.description('Update a book by id from database')
@openapi.body({'application/json': create_book_json_schema})
@validate_with_jsonschema(jsonschema=create_book_json_schema)
@protected
async def update_book_by_id(request, book_id: str, username: str):
    existing_book = _db.get_book_by_id(book_id)
    if not existing_book:
        raise ApiNotFound(f'Book with id {book_id} not found')
    if existing_book.owner != username:
        raise ApiForbidden('You are not the owner of this book')
    body = request.json
    book = Book(book_id).from_dict(body)
    book.owner = existing_book.owner
    book.last_updated_at = int(time.time())
    book.created_at = existing_book.created_at
    updated = _db.update_book_by_id(book_id, book)
    if updated.matched_count == 0:
        raise ApiNotFound(f'Book with id {book_id} not found')
    if not updated:
        raise ApiInternalError('Fail to update book')

    await request.app.ctx.cache.delete(CacheConstants.all_books)
    
    return json({'data': {
        'message': 'updated',
        'book': book.to_dict()
    }})


# DELETE /books/{id}
@books_bp.delete('/<book_id:str>')
@openapi.tag('Books')
@openapi.summary('Delete a book by id')
@openapi.description('Delete a book by id from database')
@protected
async def delete_book_by_id(request, book_id: str, username: str):
    existing_book = _db.get_book_by_id(book_id)
    if not existing_book:
        raise ApiNotFound(f'Book with id {book_id} not found')
    if existing_book.owner != username:
        raise ApiForbidden('You are not the owner of this book')
    deleted = _db.delete_book_by_id(book_id)
    if not deleted:
        raise ApiInternalError('Fail to delete book')
    await request.app.ctx.cache.delete(CacheConstants.all_books)
    return json({'data': {
        'message': 'deleted',
        'book': existing_book.to_dict()
    }})