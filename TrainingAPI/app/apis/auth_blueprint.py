from pymongo.errors import DuplicateKeyError
from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi
from app.databases.mongodb import MongoDB
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiBadRequest, ApiUnauthorized
from app.utils.jwt_utils import generate_jwt
from app.utils.password_utils import hash_password, verify_password

auth_bp = Blueprint('auth_blueprint', url_prefix='/auth')
_db = MongoDB()

_credentials_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string', 'minLength': 8}
    },
    'required': ['username', 'password']
}

@auth_bp.post('/register')
@openapi.tag('Auth')
@openapi.summary('Register a new user')
@openapi.description('Register a new user in database')
@openapi.body({'application/json': _credentials_schema})
@validate_with_jsonschema(jsonschema=_credentials_schema)
async def register_user(request):
    body = request.json
    username = body['username'].strip().lower()
    password = body['password']

    if not username or not password:
        raise ApiBadRequest('Username and password are required')

    if len(password) < 8:
        raise ApiBadRequest('Password must be at least 8 characters long')


    password_hash = hash_password(password)
    try:
        _db.create_user(username, password_hash)
    except DuplicateKeyError:
         raise ApiBadRequest('Username already exists')

    return json({'data': {
        'message': 'User registered successfully',
    }}, status=201)

@auth_bp.post('/login')
@openapi.tag('Auth')
@openapi.summary('Login a user')
@openapi.description('Login a user in database')
@openapi.body({'application/json': _credentials_schema})
@validate_with_jsonschema(jsonschema=_credentials_schema)
async def login_user(request):
    body = request.json
    username = body['username'].strip().lower()
    password = body['password']

    if not username or not password:
        raise ApiBadRequest('Username and password are required')

    user = _db.get_user_by_username(username)
    
    if not user:
        raise ApiUnauthorized('Invalid username or password')

    if not verify_password(password, user['password_hash']):
        raise ApiUnauthorized('Invalid username or password')
    token = generate_jwt(username)
    return json({'data': {
        'message': 'User logged in successfully',
        'token': token
    }}, status=200)