from db import connect
from db.model import Basic, Rating
import pandas as pd


class BasicFactory:
    def __init__(self):
        self.ignore = ['video', 'videoGame', 'tvEpisode']

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
            return pd.read_sql(query.statement, session.bind)
        finally:
            session.close()

    @staticmethod
    def save(records):
        """
        Save records

        :param list[Basic] or Basic records: records
        """
        session = connect()

        try:
            if isinstance(records, list):
                for record in records:
                    session.merge(record)
            else:
                session.merge(records)
            session.commit()
        finally:
            session.close()
