import pandas as pd


def get_data(offline):
    if offline:
        df_title = pd.read_csv('imdb/data/title.basics.tsv', sep='\t')
        df_ratings = pd.read_csv('imdb/data/title.ratings.tsv', sep='\t')
    else:
        df_title = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')
        df_ratings = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', sep='\t')

    df_merged = df_title.merge(df_ratings, on='tconst')
    df_merged = df_merged[df_merged.titleType.notnull()]
    df_merged = df_merged[~df_merged.titleType.isin(['video', 'videoGame'])]

    return df_merged
