from db import Base
from sqlalchemy import Boolean, Column, Integer, String, Text


class Basic(Base):
    __tablename__ = 'basics'

    title_id = Column('title_id', String(10), primary_key=True)
    title_type = Column('title_type', String(250))
    primary_title = Column('primary_title', String(250))
    original_title = Column('original_title', String(250))
    is_adult = Column('is_adult', Boolean)
    start_year = Column('start_year', Integer)
    end_year = Column('end_year', Integer)
    runtime = Column('runtime', Integer)
    genres = Column('genres', String(50))
    description = Column(Text)
    image_url = Column(Text)
    is_crawled = Column('is_crawled', Boolean, default=False)
