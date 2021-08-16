from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String, select

import secrets

from server.app import Base, async_session as session
from ._basic_model import BasicModel


class Token(Base, BasicModel):
    __tablename__ = 'tokens'

    id = Column(BigInteger, primary_key=True)
    token = Column(Text, unique=True)
    type = Column(String, default='one-time')
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, token, token_type) -> None:
        self.token = token
        self.type = token_type

    @staticmethod
    async def generate_unique_token():
        token = secrets.token_urlsafe(1024)
        fails = 0
        while True:
            exists = await Token.get_by_token(token)
            if not exists:
                break
            fails += 1
            if fails > 15:
                return ''
            token = secrets.token_urlsafe(1024)
        return token

    @staticmethod
    async def get_by_token(token):
        async with session() as s:
            statement = select(Token).where(Token.token == token)
            resp = await s.execute(statement)
            
            obj = resp.first()
            return obj[0] if obj else None

    @staticmethod
    async def get(id):
        async with session() as s:
            return await s.get(Token, id)
    
    def as_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'type': self.token,
            'creation_date': self.created_date.isoformat(timespec='hours')
        }
