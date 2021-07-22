from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger(), primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    key = db.Column(db.Text(), nullable=False, unique=True)

