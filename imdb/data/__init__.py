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

    return df_merged
