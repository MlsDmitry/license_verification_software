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


bp = Blueprint('license_verification_api')


def fail(msg=None, status_code=201):
    if msg:
        return json(
            {'status': 'request failed', 'message': msg},
            status=status_code)
    return json({'status': 'request failed'}, status=status_code)


def success(msg=None, data: dict = None, status_code=201):
    resp = {'status': 'success'}
    if msg:
        resp.update({'message': msg})
    if data:
        resp.update(data)
    return json(resp, status=status_code)


def auth_admin(request):
    if 'master_key' not in request.json:
        return False

    if request.json['master_key'] != os.environ['MASTER_PASSWORD']:
        return False

    return True


async def handle_token(request):
    if not auth_admin(request):
        return False

    unique_token = await Token.generate_unique_token()
    token = Token(unique_token, 'one-time')

    commit_success = await token.add()
    if not commit_success:
        return False

    return token


async def handle_client(request):
    if 'sid' not in request.json:
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

    if 'name' in request.json:
        user.name = request.json['name']

    if not User.check_sid(request.json['sid']):
            return False
    uid = User.parse_sid(request.json['sid'])

    user.sid = uid
    user.salt = uuid.uuid4().hex

    encrypted_key = generate_signature(user.sid + user.salt)
    encoded_key = b64encode(encrypted_key).decode('ascii')

    user.encrypted_license_key = encoded_key

    commit_success = await user.add()
    if not commit_success:
        return False

    return user


@bp.post("/register")
async def register(request):
    if 'type' not in request.json:
        return fail()

    if request.json['type'] == 'one-time token':
        token = await handle_token(request)
        if not token:
            return fail()

        return success(data={'id': token.id, 'token': token.token})
    elif request.json['type'] == 'workstation':
        user = await handle_client(request)
        if not user:
            return fail()

        return success(data={'id': user.id, 'key': user.encrypted_license_key})

    return fail()


@bp.post('/login')
async def login(request):
    if 'key' not in request.json or 'sid' not in request.json:
        return fail()

    if not User.check_sid(request.json['sid']):
        return fail()
    
    sid = User.parse_sid(request.json['sid'])
    
    key = b''
    try:
        key = b64decode(request.json['key'].encode('ascii'))
    except Exception as e:
        print(e)
        return fail()

    user = await User.get_by_key(request.json['key'])
    if not user:
        return fail()

    try:
        if not verify_signature(f'{sid}{user.salt}', key):
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

    user = await User.get_by_key(request.json['key'])
    if not user:
        return fail()
    # delete
    commit_success = await user.delete()
    if not commit_success:
        return fail()

    return success()
