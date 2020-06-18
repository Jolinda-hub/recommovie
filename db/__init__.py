from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def connect():
    """
    :return: database session
    :rtype: sqlalchemy.orm.session.Session
    """
    conn_args = {'check_same_thread': False}
    engine = create_engine(
        'sqlite:///recommendation.db',
        connect_args=conn_args
    )
    return sessionmaker(bind=engine)()
