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
        self.logger.info('Inserting records to data...')
        try:
            df.to_sql(name='movies', con=session.bind, if_exists='append', chunksize=50000, index=False)
        finally:
            session.close()

    def get_dataframe(self):
        """
        Get movies for recommendation

        :return: dataframe contains movie id, genre and description
        :rtype: dataframe
        """
        self.logger.info('Fetching movie records...')
        session = connect()

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

    def get_items(self):
        """
        Get items for insert to elasticsearch

        :return: dataframe contains movie id, genre and description
        :rtype: dataframe
        """
        self.logger.info('Fetching movie records...')
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

    def get_movies(self, movie_ids=None):
        """
        Get movies for homepage or recommendation page

        :return: last added 6 movies
        :rtype: list
        """
        self.logger.info('Getting movies...')
        session = connect()

        if movie_ids is not None:
            filters = [
                Movie.movie_id.in_(movie_ids),
            ]

            order_ = None
            limit_ = 12
        else:
            filters = [
                Movie.kind == 'movie',
                Movie.image_url.isnot(None),
            ]

            order_ = Movie.movie_id.desc()
            limit_ = 6

        try:
            return session.query(Movie).filter(*filters).order_by(order_).limit(limit_).all()
        finally:
            session.close()

    def get_result(self, query):
        """
        Get result of sql query

        :param str query: sql query
        :return: columns and data
        :rtype: ([cols], [data])
        """
        self.logger.info('Getting sql query results...')
        session = connect()

        try:
            result = session.execute(query)
            cols = result.keys()
            data = result.fetchall()
            return cols, data
        finally:
            session.close()
