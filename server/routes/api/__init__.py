
from sanic.blueprints import Blueprint
from .license_verification import bp as license_verification_route

api_group = Blueprint.group(license_verification_route, url_prefix='/api')
