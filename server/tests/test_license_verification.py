import sys
from os import getcwd
sys.path.append(getcwd())

from server.app import create_application
import pytest

@pytest.fixture
def app():
    app = create_application()
    yield app


@pytest.fixture
def server(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


async def test_index(server):
    resp = await server.post('/api/login')
    assert resp.status_code == 422


async def test_player(server):
    resp = await server.post('/api/register')
    assert resp.status_code == 422
