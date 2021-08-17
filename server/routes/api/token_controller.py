import os
from server.models import Token
from sanic.response import json
from sanic import Blueprint

bp = Blueprint('token_controller', url_prefix='/token')


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
    if not request.json:
        return fail(status_code=422)


@bp.middleware('request')
def auth_check(request):
    if 'master_key' not in request.json:
        return fail(status_code=401)

    if request.json['master_key'] != os.environ['MASTER_PASSWORD']:
        return fail(status_code=401)


@bp.post('/')
async def token(request):
    unique_token = await Token.generate_unique_token()
    token = Token(unique_token, 'one-time')
    commit_success = await token.add()
    if not commit_success:
        return fail()
    return success(data={'token': token.token})


@bp.post('/<token_id:int>/delete')
async def delete(request, token_id):
    token = await Token.get(token_id)
    if not token:
        return fail('Token not found', 404)

    commit_sucess = await Token.delete(token)
    if not commit_sucess:
        return fail('Token not deleted', status_code=201)

    return success(status_code=200)
