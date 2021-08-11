from gino.ext.sanic import Gino
import asyncio
import uvloop
from sanic import Sanic
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

from . import key_manager
from .models import Base

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

async def init_db():
    global engine, async_session
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.environ['USER']}:{os.environ['PASSWORD']}@database/{os.environ['DATABASE']}", echo=True,
    )
    # engine = create_async_engine(
    #     f"sqlite+asyncpg:///verification_database.db", echo=True,
    # )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    await engine.dispose()
    

def create_application():
    global db
    
    # load environment variables from .env file
    load_dotenv(os.path.join("server", "server.env"))
    
    app = Sanic("Verification_server")

    # app.config.DB_HOST = 'localhost'
    # app.config.DB_DATABASE = 'verification_database'
    
    # setup database
    # db = Gino()
    # db.init_app(app)
    # setup database models
    from . import models
    loop.run_until_complete(init_db())
    # generate public and private keys
    key_manager.setup_keys(save_to_file=True)
    key_manager.setup_keys(save_to_file=False) 
    
    from . import api
    app.blueprint(api.api_group)

    return app
    
    