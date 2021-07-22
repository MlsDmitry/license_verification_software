from sanic.response import text
from sanic import Blueprint

bp = Blueprint(__name__)

@bp.post("/register")
async def register(request):
    
    return text('201', status=201)
    # return text(f'Hello form registration. \
    #             Master token is {master_token} \
    #             Email is {email} \
    #             ')

@bp.get("/register")
async def register(request):
    return text(f'Hello form registration.')