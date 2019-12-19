# -*- coding: utf-8 -*-
from db import connect
from db.models import Movie
from util import Util
import pandas as pd

util = Util()


class DataOperation:
    def __init__(self):
        self.logger = util.set_logger('db connection')

    def insert(self, df):
        """
        Insert data

        :param dataframe df: dataframe for writing
        """
        session = connect()
        self.logger.info('Inserting records to data')

        args = {
            'name': 'movies',
            'con': session.bind,
            'if_exists': 'append',
            'index': False,
        }
        try:
            df.to_sql(**args)
        finally:
            session.close()

    def get_dataframe(self):
        """
        Get movies for recommendation

        :return: dataframe contains movie id, genre and description
        :rtype: dataframe
        """
        self.logger.info('Fetching movie records')
        session = connect()

        cols = [
            Movie.movie_id,
            Movie.title,
            Movie.start_year,
            Movie.genres,
            Movie.description,
            Movie.kind,
            Movie.runtime,
            Movie.num_votes,
            Movie.image_url,
            Movie.average_rating,
        ]

        filters = [
            Movie.runtime.isnot(None),
            Movie.genres.isnot(None),
            Movie.description.isnot(None),
        ]

        query = session.query(*cols) \
            .filter(*filters) \
            .order_by((Movie.average_rating * Movie.num_votes).desc())

        try:
            return pd.read_sql(query.statement, session.bind)
        finally:
            session.close()

    def get_items(self):
        """
        Get items for insert to elasticsearch

        :return: dataframe contains movie id, genre and description
        :rtype: dataframe
        """
        self.logger.info('Fetching movie records')
        session = connect()

        cols = [
            Movie.movie_id,
            Movie.primary_title,
            Movie.start_year
        ]

        try:
            return session.query(*cols).all()
        finally:
            session.close()
