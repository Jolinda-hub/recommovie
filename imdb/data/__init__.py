from db import connect
from db.factory import TableFactory
from util import get_params, set_logger
import numpy as np
import pandas as pd
import re

config = get_params()
tf = TableFactory()
logger = set_logger('imdb data')

path_config = {
    'basics': f"{config['crawler']['path']}/title.basics.tsv.gz",
    'episodes': f"{config['crawler']['path']}/title.episode.tsv.gz",
    'ratings': f"{config['crawler']['path']}/title.ratings.tsv.gz"
}

mapping = {
    'tconst': 'title_id',
    'runtimeMinutes': 'runtime',
    'parentTconst': 'parent_id'
}

title_types = {
    'movie': 1,
    'tvSeries': 2,
    'tvMiniSeries': 3,
    'tvMovie': 4,
    'short': 5,
    'tvShort': 6,
    'tvSpecial': 7
}


def edit(columns):
    """
    Edit column names for inserting to db

    :param list columns: column names from csv
    :return: edited column names
    :rtype: list
    """
    names = []

    for column in columns:
        # to snake case
        edited = re.sub(r'(?<!^)(?=[A-Z])', '_', column).lower()

        # name mapping
        if column in mapping.keys():
            edited = mapping[column]
        names.append(edited)

    return names


def insert():
    """
    Insert to db
    """
    chunk_size = 50000

    for table, path in path_config.items():
        session = connect()
        previous = tf.get_by_table_name(name=table)
        counter = 0
        logger.info(f'Reading data from csv for {table}')

        # quoting=3: QUOTE_NONE
        for chunk in pd.read_csv(
                path,
                chunksize=chunk_size,
                sep='\t',
                quoting=3
        ):
            # camel-case to snake-case
            chunk.columns = edit(chunk.columns)

            titles = ['video', 'videoGame', 'tvEpisode']
            cond1 = True

            # remove some title types
            # title type mapping
            if table == 'basics':
                cond1 = ~chunk.title_type.isin(titles)
                chunk['title_type'] = chunk['title_type'].replace(title_types)

            cond2 = ~chunk.title_id.isin(previous)
            chunk = chunk[cond1 & cond2]

            if len(chunk) == 0:
                continue

            counter += len(chunk)

            args = {
                'name': table,
                'con': session.bind,
                'if_exists': 'append',
                'index': False
            }
            try:
                chunk.replace('\\N', np.nan).to_sql(**args)
            finally:
                session.close()

            logger.info(f'{counter} rows have been written to the {table}')

        logger.info(f'Operation done for {table}')
