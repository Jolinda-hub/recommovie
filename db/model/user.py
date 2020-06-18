from db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP as Timestamp
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(100), nullable=False)
    email = Column('email', String(50), nullable=False)
    password = Column('password', String(200), nullable=False)
    created_at = Column('created_at', Timestamp, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
