from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

import datetime
import secrets

from . import Base

class Token(Base):
    __tablename__ = 'tokens'
    
    id = Column(BigInteger, primary_key=True)
    token = Column(Text, unique=True)
    type = Column(String, default='one-time')
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    def generate_token(self):
        return secrets.token_urlsafe(1024)