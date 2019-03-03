# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float, String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, index=True)
    genre = Column(String(50), nullable=True, index=True)
    kind = Column(Boolean, nullable=True, index=True)
    description = Column(Text, nullable=True, index=True)
    url = Column(Text, nullable=True, index=True)
    rating = Column(Float, nullable=True)
    year = Column(Integer, nullable=True)


class Recommendation(Base):
    __tablename__ = 'recommendation'

    id = Column(Integer, primary_key=True)
    recommend_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)


# Create only once
engine = create_engine('sqlite:///recommendation.db')
Base.metadata.create_all(engine)
