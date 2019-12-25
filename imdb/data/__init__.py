import pandas as pd


def get_data(n):
    """
    :return: data frame contains movies information
    :rtype: pd.DataFrame
    """
    args = {
        'sep': '\t',
        'low_memory': False,
    }
    df_title = pd.read_csv('imdb/data/title.basics.tsv.gz', **args)
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

    :param dataframe df: all movies
    :return: dataframe with scores
    :rtype: dataframe
    """
    df.loc[:, 'score'] = df['averageRating'] * df['numVotes']
    return df.sort_values(by='score', ascending=False).drop('score', axis=1)
