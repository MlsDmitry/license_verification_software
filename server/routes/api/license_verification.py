from sanic import response
from sanic.response import json, text
from sanic import Blueprint

from base64 import b64encode, b64decode
from sqlalchemy import select
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.operators import exists

import os
import uuid

from server.models import User, Token
from server.key_manager import generate_signature, verify_signature


bp = Blueprint(__name__)

def fail(msg=None):
    if msg:
        return json({'status': 'request failed', 'message': msg}, status=201)
    return json({'status': 'request failed'}, status=201)


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
        
    commit_success = await token.add()
    if not commit_success:
        return False
        
    return token
        

async def handle_client(request):
    if 'uuid' not in request.json:
        return False
    
    if 'token' in request.json:
        token = request.json['token']
        token = await Token.get_by_token(token)
        if not token:
            return False
        # remove token
        commit_success = await token.delete()
        if not commit_success:
            return False
    elif not auth_admin(request):
            return False
        
    user = User()
    
    if 'email' in request.json:
        user.email = request.json['email']
        
    if 'activated' in request.json:
        user.activated = bool(request.json['activated'])
    
    if 'name' in request.json:
        user.name = request.json['name']
    
    uid = User.parse_uuid(request.json['uuid'])
    
    if not User.check_uuid(uid):
        return False
    
    user.uuid = uid
    user.salt = uuid.uuid4().hex
    
    encrypted_key = generate_signature(user.uuid + user.salt)
    encoded_key = b64encode(encrypted_key).decode('ascii')
    
    user.encrypted_license_key = encoded_key
    
    commit_success = await user.add()
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
        
        return json({'status': 'success', 'token': token.token}, status=201)
    elif request.json['type'] == 'workstation':
        key = await handle_client(request)
        if not key:
            return fail()
        
        return json({'status': 'success', 'license_key': key}, status=201)
        
    return fail()
            
@bp.post('/login')
async def login(request):
    if ['key', 'uuid'] not in request.json:
        return fail()
    
    uuid = User.parse_uuid(request.json['uuid'])
    if not User.check_uuid(uuid):
        return fail()
    
    key = b''
    try:
        key = b64decode(request.json['key']).encode('ascii')
    except Exception as e:
        print(e)
        return fail()
    
    # if len(key) != 256:
    #     return fail()
    
    
    user = User.get_by_key(request.json['key'])
    if not user:
        return fail()
    
    try:
        if not verify_signature(f'uuid{user.salt}', key):
            return fail()
    except Exception as e:
        print(e)
        return fail()
    
    # check if user account has been suspended
    if user.suspended:
        return fail()
    
    return json({'status': 'success'}, status=201)


@bp.post('/deregister')
async def deregister_license(request):
    if not auth_admin(request):
        return fail()
    
    if 'key' not in request.json:
        return fail('No license key provided')
    
    user = User.get_by_key(request.json['key'])
    if not user:
        return fail()
    # delete
    commit_success = await user.delete()
    if not commit_success:
        return fail()
    
    return json({'status': 'success'}, status=201)

@bp.post('/activate')
async def activate(request):
    if not auth_admin(request):
        fail()
        
    
    
    
