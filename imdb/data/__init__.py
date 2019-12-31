import gzip
import pandas as pd


def get_data(n, update):
    """
    :param int n: top n movies
    :param bool update: is update or crawling

    :return: data frame contains movies information
    :rtype: pd.DataFrame
    """
    n_lines = 0

    if update:
        n_lines = sum(1 for _ in gzip.open('imdb/data/title.basics.tsv.gz'))

    args = {
        'sep': '\t',
        'low_memory': False,
        'skiprows': range(1, n_lines - 1000)
    }
    df_title = pd.read_csv('imdb/data/title.basics.tsv.gz', **args)
    args.pop('skiprows', None)
    df_ratings = pd.read_csv('imdb/data/title.ratings.tsv.gz', **args)

    merged = df_title.merge(df_ratings, on='tconst')
    merged = merged[merged.titleType.notnull()]

    types = ['video', 'videoGame', 'tvEpisode']
    merged = merged[~merged.titleType.isin(types)]

    # if set n to False, get all movies
    if not n:
        return merged

    return generate_score(merged)[:n]


def generate_score(df):
    """
    Generate scores of movies

    :param pd.DataFrame df: all movies
    :return: data frame with scores
    :rtype: pd.DataFrame
    """
    df.loc[:, 'score'] = df['averageRating'] * df['numVotes']
    return df.sort_values(by='score', ascending=False).drop('score', axis=1)
