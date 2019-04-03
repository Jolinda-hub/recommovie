import pandas as pd


def get_data():
    """
    :return: dataframe contains movies information
    :rtype: dataframe
    """
    df_title = pd.read_csv('imdb/data/title.basics.tsv', sep='\t')
    df_ratings = pd.read_csv('imdb/data/title.ratings.tsv', sep='\t')

    df_merged = df_title.merge(df_ratings, on='tconst')
    df_merged = df_merged[df_merged.titleType.notnull()]
    df_merged = df_merged[~df_merged.titleType.isin(['video', 'videoGame', 'tvEpisode'])]

    df_selected = generate_score(df_merged)

    return df_selected


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
