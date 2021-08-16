from sqlalchemy import select
from sanic import Blueprint, request
from sanic.response import json, text
import os

from server.models import User, Token

bp = Blueprint(__name__)

def auth_admin(request):
    master_key = request.form.get('masterkey')
    return os.environ['MASTER_PASSWORD'] == master_key
    
@bp.post('/show')
async def show(request):
    if not auth_admin(request):
        return text('', status=422)
        
    action = request.form.get('action')
    if not action:
        return text('', status=422)
    
    if action == 'showtokens':
        async with async_session() as session:
            statement = select(Token)
            response = await session.execute(statement)
            # for token in response.all():
            
            return json(list(map(lambda token: token[0].as_dict(), response.all())), status=201)
            # return text('', status=201)
    elif action == 'showlicensekeys':
        async with async_session() as session:
            statement = select(User.name, User.email, User.uuid, User.activated, User.suspended, User.created_date)
            response = await session.execute(statement)
            return json(response.all(), status=201)

@bp.delete("/token/delete")
async def delete_token(request):
    if not auth_admin(request):
        return text('', status=422)
    
    token = request.form.get('token')
    if not token:
        return text('', status=422)
    