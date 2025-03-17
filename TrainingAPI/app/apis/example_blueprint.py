from sanic import Blueprint, text
from sanic.response import json
from sanic_ext import openapi

example = Blueprint('example_blueprint', url_prefix='/ping')


@example.route('/')
@openapi.tag('Example')
@openapi.summary('Get server status')
async def bp_root(request):
    return text("Server is online")
