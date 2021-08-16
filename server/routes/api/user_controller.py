from server.models import User
from sanic import Blueprint
from sanic.response import json, text
import os


bp = Blueprint('user_controller', url_prefix='/user')


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


@bp.get('/')
def root(request):
    return text('it\'s okay!')


@bp.post('/<user_id:int>/delete')
async def delete(request, user_id: int):
    user = await User.get(user_id)
    if not user:
        return fail('User not found', 404)

    commit_sucess = await User.delete(user)
    if not commit_sucess:
        return fail('User not deleted', status_code=204)

    return success(status_code=200)


@bp.patch('/<user_id:int>')
async def patch(request, user_id: int):
    del request.json['master_key']
    if not all(field in ['name', 'email', 'suspended']
               for field in request.json):
        return fail(msg='Cannot edit fields you specified', status_code=406)

    user = await User.get(user_id)
    if not user:
        return fail('User not found', 404)

    commit_sucess = await user.update(request.json)

    if not commit_sucess:
        return fail('User not deleted', status_code=204)

    return success(status_code=200)
