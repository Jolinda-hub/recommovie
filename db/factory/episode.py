from db import connect
from db.model import Episode, Rating
from sqlalchemy import func
import pandas as pd


class EpisodeFactory:
    def get_episodes(self):
        """
        Get episodes with average ratings

        :return: episodes
        :rtype: pd.DataFrame
        """
        session = connect()

        cols = [
            Episode.title_id,
            Episode.parent_id,
            Episode.info.label('episodes')
        ]

        filters = [
            Episode.episode_number.isnot(None),
            Episode.season_number.isnot(None)
        ]

        orders = [
            Episode.parent_id,
            Episode.season_number,
            Episode.episode_number
        ]

        subquery = session \
            .query(*cols) \
            .filter(*filters) \
            .order_by(*orders) \
            .subquery('sub')

        cols = [
            subquery.c.parent_id.label('title_id'),
            func.group_concat(Rating.average_rating).label('episode_ratings'),
            func.group_concat(subquery.c.episodes).label('episode_info')
        ]

        query = session \
            .query(*cols) \
            .join(subquery, subquery.c.title_id == Rating.title_id) \
            .group_by(subquery.c.parent_id)

        try:
            return pd.read_sql(query.statement, session.bind)
        finally:
            session.close()
