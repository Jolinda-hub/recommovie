from db import Base
from sqlalchemy import cast, Column, ForeignKey, Integer, String
from sqlalchemy.orm import column_property


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
