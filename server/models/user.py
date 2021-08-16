from os import stat
from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String, select

from ._basic_model import BasicModel
from server.app import async_session as session, Base


class User(Base, BasicModel):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    name = Column(String, unique=False, nullable=True, default='')
    email = Column(String, unique=True, nullable=True, default='')
    uuid = Column(String, nullable=False, unique=True)
    salt = Column(String, nullable=False, unique=True)
    encrypted_license_key = Column(Text, nullable=False, unique=True)
    suspended = Column(Boolean, default=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    # __mapper_args__ = {"eager_defaults": True}

    def __init__(self, name='', email='', uuid='', salt='',
                 encrypted_license_key='', suspended=False):
        self.uuid = uuid
        self.salt = salt
        self.encrypted_license_key = encrypted_license_key
        self.name = name
        self.email = email
        self.suspended = suspended

    @staticmethod
    async def get_by_key(key):
        async with session() as s:
            statement = select(User).where(User.encrypted_license_key == key).limit(1)
            resp = await s.execute(statement)
            
            obj = resp.first()
            return obj[0] if obj else None

    @staticmethod
    def check_uuid(uuid: str):
        return len(uuid) == 32

    @staticmethod
    def parse_uuid(uuid: str):
        return ''.join(uuid.split('-'))
    
    @staticmethod
    async def get(id):
        async with session() as s:
            return await s.get(User, id)
    
    @staticmethod
    async def all():
        async with session() as s:
            statement = select(User)
            resp = await s.execute(statement)
            
            objs = resp.all()
            return objs if len(objs) > 0 else None

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'key': self.encrypted_license_key,
            'suspended': self.suspended,
            'creation_date': self.created_date.isoformat(timespec='hours')
        }