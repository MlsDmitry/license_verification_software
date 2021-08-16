from sanic.response import json
from sanic.blueprints import Blueprint
from .license_verification import bp as license_verification_bp
from .token_controller import bp as token_controller_bp
from .user_controller import bp as user_controller_bp

api_routes = Blueprint.group(
    license_verification_bp,
    user_controller_bp,
    token_controller_bp,
    url_prefix='/api')


@api_routes.middleware('request')
def json_presence_check(request):
    if not request.json:
        return json({'status': 'request failed'}, status=422)
