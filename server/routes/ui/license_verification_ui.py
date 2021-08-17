from sanic import Blueprint, request
from sanic.response import json, text
import os

from server.models import User, Token

bp = Blueprint("license_verification_ui")


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


@bp.middleware('request')
def json_presence_check(request):
    if not request.form:
        print('failed form check')
        return fail(status_code=422)


@bp.middleware('request')
def auth_admin(request):
    master_key = request.form.get('master_key')
    if not os.environ['MASTER_PASSWORD'] == master_key:
        print('wrong master password')
        return fail(status_code=401)


@bp.post('/show')
async def show(request):
    action = request.form.get('action')
    if not action:
        print('didn\' find action')
        return fail(status_code=422)

    if action == 'showtokens':
        tokens = await Token.all()
        if not tokens:
            return fail('No tokens found')

        data = list(map(lambda t_token: t_token[0].as_dict(), tokens))
        print(data)
        return success(data={'data': data})
    elif action == 'showusers':
        users = await User.all()
        if not users:
            return fail('No users found')

        data = list(map(lambda t_user: t_user[0].as_dict(), users))
        print(data)
        return success(data={'data': data})

    return fail('Undefined action')
