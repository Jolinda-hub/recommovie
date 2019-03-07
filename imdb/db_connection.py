# -*- coding: utf-8 -*-
from models import Movie
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os
import pandas as pd

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)


class DbConnection:
    def __init__(self):
        self.logger = logging.getLogger('IMDB - DbConnection Class')

    def connect(self):
        """
        :return: database session
        :rtype: sqlalchemy.orm.session.Session
        """
        self.logger.info('Connecting to sqlite...')
        conn_args = {'check_same_thread': False}
        engine = create_engine('sqlite:///../recommendation.db', connect_args=conn_args)
        return sessionmaker(bind=engine)()

    def insert(self, df):
        """
        :param dataframe df: dataframe for writing
        """
        session = self.connect()
        self.logger.info('Inserting records to data...')
        try:
            df.to_sql(name='movies', con=session.bind, if_exists='append', chunksize=50000, index=False)
        finally:
            session.close()

    def get_dataframe(self):
        """
        :return: dataframe contains movie id, genre and description
        :rtype: dataframe
        """
        self.logger.info('Fetching movie records...')
        session = self.connect()

        cols = [
            Movie.movie_id,
            Movie.title,
            Movie.start_year,
            Movie.genres,
            Movie.description,
            Movie.kind,
        ]

        filters = [
            Movie.description.isnot(None),
            Movie.genres.isnot(None),
        ]

        query = session.query(*cols).filter(*filters).order_by(Movie.start_year.desc())

        try:
            return pd.read_sql(query.statement, session.bind)
        finally:
            session.close()

    def get_movies(self):
        """
        :return: last added 6 movies
        :rtype: list
        """
        session = self.connect()

        try:
            return session.query(Movie) \
                .filter(Movie.kind == 'movie') \
                .filter(Movie.image_url.isnot(None)) \
                .order_by(Movie.movie_id.desc()).limit(6).all()
        finally:
            session.close()
