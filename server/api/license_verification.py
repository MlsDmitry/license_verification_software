from sanic import response
from sanic.response import json, text
from sanic import Blueprint

import os
import uuid
from base64 import b64encode, b64decode
from sqlalchemy import select
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import user
from server.models import User, Token
from server.key_manager import generate_signature, verify_signature
from server.app import async_session

bp = Blueprint(__name__)

def fail():
    return json({'status': 'request failed'}, status=201)

async def safe_add(obj):
    async with async_session() as session:
        try:
            session.add(obj)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(e)
            return False

    return True

def parse_uuid(uuid: str):
    return ''.join(uuid.split('-'))

async def safe_delete(obj):
    async with async_session() as session:
        try:
            await session.delete(obj)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(e)
            return False
    return True

def auth_admin(request):
    if 'master_key' not in request.json:
        return False
    
    if request.json['master_key'] != os.environ['MASTER_PASSWORD']:
        return False

    return True


async def handle_token(request):
    if not auth_admin(request):
        return False
    
    token = Token()
    token.token = token.generate_token()
    token.type = 'one-time'
    fails = 0
    async with async_session() as session:
        statement = select(Token).where(Token.token == token.token)
        response = await session.execute(statement)
        if not response:
            return False
        while len(response.scalars().all()) != 0:
            response = await session.execute(statement)
            if not response:
                return False
            if fails > 15:
                return False
            token.token = token.generate_token()
            fails += 1
        
    commit_success = await safe_add(token)
    if not commit_success:
        return False
        
    return token.token

async def check_token(token: str):
    async with async_session() as session:
        statement = select(Token).where(Token.token == token)
        response = await session.execute(statement)
        if not response:
            return False
        tokens = response.scalars().all()
        print(tokens)
        if len(tokens) != 1:
            return False
        
    commit_success = await safe_delete(tokens[0])
    if not commit_success:
        return False
        
    return True
        

async def handle_client(request):
    if 'uuid' not in request.json:
        return False
    
    if 'token' in request.json:
        token = request.json['token']
        is_valid = await check_token(token)
        if not is_valid:
            return False
    elif not auth_admin(request):
            return False
        
    user = User()
    
    if 'email' in request.json:
        user.email = request.json['email']
        
    if 'activated' in request.json:
        user.activated = bool(request.json['activated'])
    
    uid = parse_uuid(request.json['uuid'])
    if not User.check_uuid(uid):
        return False
    user.uuid = uid
    user.salt = uuid.uuid4().hex
    encrypted_key = generate_signature(user.uuid + user.salt)
    encoded_key = b64encode(encrypted_key).decode('ascii')
    user.encrypted_license_key = encoded_key
    commit_success = await safe_add(user)
    if not commit_success:
        return False
    
    return encoded_key
    
            

@bp.post("/register")
async def register(request):
    if 'type' not in request.json:
        return fail()
    
    if request.json['type'] == 'one-time token':
        token = await handle_token(request)
        if not token:
            return fail()
        
        return json({'status': 'success', 'token': token}, status=201)
    elif request.json['type'] == 'workstation':
        key = await handle_client(request)
        if not key:
            return fail()
        
        return json({'status': 'success', 'license_key': key}, status=201)
        
    return fail()
    # return json({'status': 'success', 'license_key': user.encrypted_license_key}, status=201)
            
@bp.post('/login')
async def login(request):
    if 'key' not in request.json:
        return fail()
    
    if 'uuid' not in request.json:
        return fail()
    
    uuid = parse_uuid(request.json['uuid'])
    if not User.check_uuid(uuid):
        return False
    
    key = b''
    try:
        key = b64decode(request.json['key'])
    except Exception as e:
        print(e)
        return fail()
    
    if len(key) != 256:
        return fail()
    
    
    async with async_session() as session:
        print('183')
        statement = select(User).where(User.encrypted_license_key == request.json['key'])
        response = await session.execute(statement)
        if not response:
            return fail()
        
        users_list = response.scalars().all()
        
        if len(users_list) != 1:
            return fail()
        
        user = users_list[0]
        
        try:
            if not verify_signature(uuid + user.salt, b64decode(request.json['key'].encode('ascii'))):
                return fail()
        except Exception as e:
            print(e)
            return fail()
    
    return text('201', status=201)
    # return text(f'Hello form registration. \
    #             Master token is {master_token} \
    #             Email is {email} \
    #             ')
    return json({'status': 'success'}, status=201)

  
@bp.get("/register")
async def register(request):
    return text(f'Hello form registration.')