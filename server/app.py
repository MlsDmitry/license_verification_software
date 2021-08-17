import asyncio
import uvloop
from sanic import Sanic
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, Query, Mapper, declarative_base
from sanic_cors import CORS, cross_origin
from dotenv import load_dotenv
import os

from . import key_manager


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
Base = declarative_base()


def _get_query_cls(mapper, session):
    if mapper:
        m = mapper
        if isinstance(m, tuple):
            m = mapper[0]
        if isinstance(m, Mapper):
            m = m.entity

        try:
            return m.__query_cls__(mapper, session)
        except AttributeError:
            pass
    return Query(mapper, session)


async def init_db():
    global engine, async_session
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.environ['DBUSER']}:{os.environ['DBPASSWORD']}@{os.environ['IP']}/{os.environ['DATABASE']}",
        echo=True,
    )

    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        query_cls=_get_query_cls)

    from . import models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


def create_application():
    global db

    # load environment variables from .env file
    load_dotenv(os.path.join("server", "example.env"))

    app = Sanic("Verification_server")

    loop.run_until_complete(init_db())

    CORS(app)
    # generate public and private keys
    key_manager.setup_keys(save_to_file=True)

    from .routes import license_verificiton_ui_bp, api_routes
    app.blueprint(license_verificiton_ui_bp)
    app.blueprint(api_routes)

    return app
