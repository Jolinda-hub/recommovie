from sqlalchemy import (
    Boolean, cast, Column, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property
from sqlalchemy import create_engine

Base = declarative_base()


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


class Episode(Base):
    __tablename__ = 'episodes'

    title_id = Column('title_id', String(9), primary_key=True)
    parent_id = Column('parent_id', String(9), ForeignKey('basics.title_id'))
    season_number = Column('season_number', Integer)
    episode_number = Column('episode_number', Integer)
    info = column_property(
        'S' +
        cast(season_number, String) +
        'E' +
        cast(episode_number, String)
    )


class Rating(Base):
    __tablename__ = 'ratings'

    title_id = Column('title_id', String(9), primary_key=True)
    average_rating = Column('average_rating', Float)
    num_votes = Column('num_votes', Integer)


# Create only once
engine = create_engine('sqlite:///recommendation.db')
Base.metadata.create_all(engine)