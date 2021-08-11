from . import db
from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

class User(db.Model):
import datetime
import secrets

from . import Base

class User(Base):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger(), primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    key = db.Column(db.Text(), nullable=False, unique=True)

    id = Column(BigInteger, primary_key=True)
    email = Column(String, unique=True)
    uuid = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    encrypted_license_key = Column(Text, nullable=False, unique=True)
    activated = Column(Boolean, default=False)
    suspended = Column(Boolean, default=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    def check_uuid(uuid: str):
        return len(uuid) == 32