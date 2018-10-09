# -*- coding: utf-8 -*-
from recommend import Recommendation
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from imdb.db_connection import DbConnection


def main():
    db = DbConnection()
    recommend = Recommendation()

    movie_df = db.get_dataframe()
    movie_df = movie_df.drop_duplicates(['name', 'year'])

    # Take sample data
    # TF-IDF can cause problems (about memory) if you get all data
    # At a time, you can only get movies or series (1=movie, 0=series)
    movie_df = movie_df[movie_df.kind == 1]

    # Create fake id for use in matrix operations
    movie_df['fake_id'] = range(1, len(movie_df) + 1)
    movie_df['genre'] = movie_df['genre'].apply(lambda x: '' if pd.isnull(x) else x)

    # Mapping between fake id and original id
    map_dict = dict()
    for idx, fake_id in zip(movie_df['id'].tolist(), movie_df['fake_id'].tolist()):
        map_dict[fake_id] = idx

    # Create cosine similarity matrix
    cosine_sim = recommend.create_matrix(movie_df)

    # Find recommended movies
    recommend_df = movie_df[['id', 'fake_id']].rename(columns={'id': 'movie_id'})
    recommend_df['recommends'] = recommend_df['fake_id'].apply(recommend.recommend, args=(cosine_sim,))

    # Recommended movies are of list type
    # Each recommended movie is rendered into one row
    rec = recommend_df.set_index(['movie_id', 'fake_id'])['recommends'].apply(pd.Series).stack()
    rec = rec.reset_index().drop('level_2', axis=1)
    rec.columns = ['movie_id', 'fake_id', 'recommend_id']

    rec['recommend_id'] = rec['recommend_id'].apply(lambda x: map_dict[x])
    db.insert_recommends(rec[['movie_id', 'recommend_id']])


if __name__ == '__main__':
    main()
