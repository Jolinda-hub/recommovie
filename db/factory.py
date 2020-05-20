from db import connect
from db.models import Basic
from db.models import Episode
from db.models import Rating
from util import set_logger
import pandas as pd


class Factory:
    def __init__(self):
        self.ignore = ['video', 'videoGame', 'tvEpisode']
        self.logger = set_logger('factory')
        self.mapping = {
            'basics': Basic,
            'episodes': Episode,
            'ratings': Rating
        }

    def get_by_table_name(self, name):
        """
        Get movie ids by table name

        :param str name: table name
        :return: movie ids
        :rtype: list
        """
        session = connect()
        table = self.mapping[name]
        query = session.query(table.title_id)

        try:
            self.logger.info(f'Getting movie ids for {name}')
            return [r[0] for r in query.all()]
        finally:
            session.close()

    def get_movie_ids(self, n=None):
        """
        Get movie ids

        :param int or None n: movie limit
        :return: movie ids
        :rtype: list
        """
        session = connect()
        filters = [
            ~Basic.title_type.in_(self.ignore),
            Basic.is_crawled.is_(False)
        ]

        query = session \
            .query(Basic.title_id) \
            .join(Rating, Rating.title_id == Basic.title_id) \
            .filter(*filters) \
            .order_by(Rating.average_rating * Rating.num_votes) \
            .limit(n)

        try:
            self.logger.info('Getting movie ids for crawling')
            return [r[0] for r in query.all()]
        finally:
            session.close()

    def get_items(self):
        """
        Get items for insert to elastic

        :return: data frame contains movie id, genre and description
        :rtype: pd.DataFrame
        """
        session = connect()
        filters = [
            ~Basic.title_type.in_(self.ignore),
            Basic.is_crawled.is_(True)
        ]

        cols = [
            Basic.title_id,
            Basic.primary_title,
            Basic.start_year,
            Rating.average_rating * Rating.num_votes
        ]

        query = session \
            .query(*cols) \
            .join(Rating, Rating.title_id == Basic.title_id) \
            .filter(*filters)

        try:
            self.logger.info('Getting items')
            return query.all()
        finally:
            session.close()

    def get_dataframe(self):
        """
        Get movies for recommendation

        :return: data frame contains movie id, genre and description
        :rtype: pd.DataFrame
        """
        session = connect()

        cols = [
            Basic.title_id,
            Basic.original_title,
            Basic.start_year,
            Basic.genres,
            Basic.description,
            Basic.title_type,
            Basic.runtime,
            Basic.image_url,
            Rating.num_votes,
            Rating.average_rating
        ]

        filters = [
            ~Basic.title_type.in_(self.ignore),
            Basic.is_crawled.is_(True),
            Basic.runtime.isnot(None),
            Basic.genres.isnot(None),
            Basic.description.isnot(None),
        ]

        query = session.query(*cols) \
            .join(Rating, Rating.title_id == Basic.title_id) \
            .filter(*filters) \
            .order_by((Rating.average_rating * Rating.num_votes).desc())

        try:
            self.logger.info('Getting all of data')
            return pd.read_sql(query.statement, session.bind)
        finally:
            session.close()

    def save(self, records):
        """
        Save records from crawling

        :param list records: records from crawling
        """
        session = connect()

        try:
            self.logger.info('Saving crawled movies to db')
            for record in records:
                instance = Basic(
                    title_id=record[0],
                    image_url=record[1],
                    description=record[2],
                    is_crawled=True
                )
                session.merge(instance)
            session.commit()
        finally:
            session.close()
