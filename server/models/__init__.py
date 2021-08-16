import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Mapper, Query


# def _get_query_cls(mapper, session):
#     if mapper:
#         m = mapper
#         if isinstance(m, tuple):
#             m = mapper[0]
#         if isinstance(m, Mapper):
#             m = m.entity

#         try:
#             return m.__query_cls__(mapper, session)
#         except AttributeError:
#             pass
#     return Query(mapper, session)

# class AsyncDatabaseSession:
#     def __init__(self):
#         self._session = None
#         self._engine = None

#     # def __getattr__(self, name):
#     #     return getattr(self._session, name)

#     async def init(self):
#         self._engine = create_async_engine(
#             f"postgresql+asyncpg://{os.environ['DBUSER']}:{os.environ['DBPASSWORD']}@{os.environ['IP']}/{os.environ['DATABASE']}",
#             echo=False,
#         )

#         await self._create_all()

#         self._session = sessionmaker(
#             self._engine, expire_on_commit=False, class_=AsyncSession, query_cls=_get_query_cls
#         )()

#         await self._engine.dispose()

#     async def _create_all(self):
#         async with self._engine.begin() as conn:
#             await conn.run_sync(Base.metadata.drop_all)
#             await conn.run_sync(Base.metadata.create_all)


# import asyncio
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# loop = asyncio.get_event_loop()

# async_database_session = AsyncDatabaseSession()
# loop.run_until_complete(async_database_session.init())

# session = async_database_session._session

from .token import Token
from .user import User
