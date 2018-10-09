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

    def __connect(self):
        """
        :return: database session
        :rtype: sqlalchemy.orm.session.Session
        """
        self.logger.info('Connecting to sqlite...')
        engine = create_engine('sqlite:///{p}/imdb/recommendation.db'.format(p=os.pardir))
        db = sessionmaker(bind=engine)
        session = db()
        return session

    def insert(self, records):
        """
        :param list records: records list
        """
        session = self.__connect()
        self.logger.info('Inserting records to data...')
        session.add_all(records)
        session.commit()

    def insert_recommends(self, df):
        """
        :param dataframe df: dataframe for writing
        """
        self.logger.info('Connecting to sqlite...')
        engine = create_engine('sqlite:///{p}/imdb/recommendation.db'.format(p=os.pardir))
        df.to_sql('recommendation', con=engine, if_exists='append', index=False)

    def get_dataframe(self):
        """
        :return: dataframe contains movie id, genre and description
        :rtype: dataframe
        """
        self.logger.info('Fetching movie records...')
        session = self.__connect()
        query = session.query(Movie.id, Movie.name, Movie.year, Movie.genre, Movie.description, Movie.kind) \
            .filter(Movie.description != '').filter(Movie.rating >= 7).filter(Movie.year > 1950) \
            .order_by(Movie.year.desc())
        return pd.read_sql(query.statement, session.bind)
