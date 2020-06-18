from db.model import Basic, Decision, Episode, Rating, User
from sqlalchemy import create_engine

if __name__ == '__main__':
    engine = create_engine('sqlite:///recommendation.db')

    tables = [
        Basic,
        Decision,
        Episode,
        Rating,
        User
    ]
    for table in tables:
        if engine.dialect.has_table(engine, table.__tablename__):
            continue

        table.__table__.create(engine)
