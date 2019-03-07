# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float, String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(String(9), primary_key=True)
    title = Column(String(250), nullable=False, index=True)
    primary_title = Column(String(250), nullable=False, index=True)
    genres = Column(String(50), nullable=True, index=True)
    kind = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True, index=True)
    image_url = Column(Text, nullable=True, index=True)
    average_rating = Column(Float, nullable=True)
    num_votes = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    is_adult = Column(Boolean, nullable=True)
    runtime = Column(Integer, nullable=True)


# Create only once
# engine = create_engine('sqlite:///recommendation.db')
# Base.metadata.create_all(engine)
