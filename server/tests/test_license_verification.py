from server.app import create_application
import pytest
import sys
from os import getcwd
from os.path import dirname
sys.path.append(getcwd())


@pytest.fixture
def app():
    app = create_application()
    yield app


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


async def test_index(test_cli):
    resp = await test_cli.post('/api/login')
    assert resp.status_code == 422


async def test_player(test_cli):
    resp = await test_cli.post('/api/register')
    assert resp.status_code == 422
