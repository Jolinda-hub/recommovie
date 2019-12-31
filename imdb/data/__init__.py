from db.data_opt import DataOperation
import pandas as pd

db = DataOperation()

PATH_BASICS = 'imdb/data/title.basics.tsv.gz'
PATH_RATINGS = 'imdb/data/title.ratings.tsv.gz'


def get_data(n):
    """
    :param int n: top n movies

    :return: data frame contains movies information
    :rtype: pd.DataFrame
    """
    old_ids = db.get_movie_ids()
    df_ratings = pd.read_csv(PATH_RATINGS, sep='\t')

    df = pd.DataFrame()
    for chunk in pd.read_csv(PATH_BASICS, chunksize=50000, sep='\t'):
        cond1 = ~chunk.titleType.isin(['video', 'videoGame', 'tvEpisode'])
        cond2 = ~chunk.tconst.isin(old_ids)
        cond3 = chunk.titleType.notnull()
        filtered = chunk[cond1 & cond2 & cond3].merge(df_ratings, on='tconst')
        df = pd.concat([df, filtered], sort=False)

    # if set n to False, get all movies
    if not n:
        return df

    return generate_score(df)[:n]


def generate_score(df):
    """
    Generate scores of movies

    :param pd.DataFrame df: all movies
    :return: data frame with scores
    :rtype: pd.DataFrame
    """
    df.loc[:, 'score'] = df['averageRating'] * df['numVotes']
    return df.sort_values(by='score', ascending=False).drop('score', axis=1)
