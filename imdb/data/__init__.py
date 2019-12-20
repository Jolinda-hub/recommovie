import pandas as pd


def get_data():
    """
    :return: dataframe contains movies information
    :rtype: dataframe
    """
    df_title = pd.read_csv('imdb/data/title.basics.tsv.gz', sep='\t')
    df_ratings = pd.read_csv('imdb/data/title.ratings.tsv.gz', sep='\t')

    df_merged = df_title.merge(df_ratings, on='tconst')
    df_merged = df_merged[df_merged.titleType.notnull()]

    types = ['video', 'videoGame', 'tvEpisode']
    df_merged = df_merged[~df_merged.titleType.isin(types)]

    return generate_score(df_merged)


def generate_score(df, n=30000):
    """
    Generate scores of movies

    :param dataframe df: all movies
    :param int n: how many movies
    :return: top n movies
    :rtype: dataframe
    """

    df.loc[:, 'movieScore'] = df['averageRating'] * df['numVotes']
    df_sorted = df.sort_values(by='movieScore', ascending=False)

    return df_sorted.head(n)
