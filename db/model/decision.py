from db import Base
from sqlalchemy import Column, Integer, String


class Decision(Base):
    __tablename__ = 'decisions'

    user_id = Column('user_id', Integer, primary_key=True)
    title_id = Column('title_id', String(9), primary_key=True)
