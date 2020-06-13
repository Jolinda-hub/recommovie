from db.factory import Factory
from scipy.signal import argrelextrema
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors.kde import KernelDensity
from sklearn.preprocessing import LabelEncoder
from util import *
import numpy as np
import random

config = get_params()
factory = Factory()


class Recommendation:
    def __init__(self):
        self.movie_df = factory.get_dataframe()
        self.episode_df = factory.get_episodes()
        self.df = None

        self.logger = set_logger('recommendation')
        self.matrix = None
        self.random_array = None

        self.create_df()
        self.preproccessing()
        self.clustering()
        self.create_matrix()
        self.create_array()

    def get_by_ids(self, movie_ids):
        """
        Get by id

        :param str or list movie_ids: movie ids
        :return: pd.Series
        """
        if isinstance(movie_ids, str):
            return self.df[self.df.title_id == movie_ids].iloc[0]

        return self.df[self.df.title_id.isin(movie_ids)].itertuples()

    def get_by_n(self, n=8):
        """
        Get first n movies

        :param int n: how many movies
        :return: first n movies
        """
        return self.movie_df.head(n).itertuples()

    def create_df(self):
        """
        Create movie data frame
        """
        self.df = self.movie_df.merge(
            self.episode_df,
            on='title_id', how='left'
        )

    def create_array(self):
        """
        Create array for random selection
        """
        filtered = self.df[self.df.image_url.notnull()]
        self.random_array = np.array(filtered[['title_id', 'num_votes']])

    def get_random(self):
        """
        Get movie by weighted random

        :return: random movie
        :rtype: pd.Series
        """
        title_id = random.choices(
            self.random_array[:, 0],
            self.random_array[:, 1]
        )[0]
        return self.df[self.df.title_id == title_id].iloc[0]

    def preproccessing(self):
        """
        Data pre-processing
        """
        le = LabelEncoder()

        # str to int with label encoder
        self.df.loc[:, 'title_type'] = le.fit_transform(self.df['title_type'])

        # drop null values
        cols = ['num_votes', 'runtime', 'start_year', 'title_type', 'genres']
        self.df = self.df.replace('', np.nan)
        self.df.dropna(subset=cols, inplace=True)

        # calculate score
        self.df.loc[:, 'score'] = (
                float(config['score']['num_votes']) * self.df['num_votes'] +
                float(config['score']['runtime']) * self.df['runtime'] +
                float(config['score']['year']) * self.df['start_year'] +
                float(config['score']['title_type']) * self.df['title_type']
        )

        self.df.reset_index(drop=True, inplace=True)

    def clustering(self):
        """
        Create clusters by movie scores
        """
        # kernel density estimation
        values = self.df['score'].values.reshape(-1, 1)
        kde = KernelDensity(kernel='gaussian', bandwidth=3).fit(values)

        # find cluster min-max points
        s = np.linspace(650, 18000)
        e = kde.score_samples(s.reshape(-1, 1))
        mi, ma = argrelextrema(e, np.less)[0], argrelextrema(e, np.greater)[0]

        # concat min-max points
        points = np.concatenate((s[mi], s[ma]), axis=0)
        buckets = []

        for point in points:
            buckets.append(point)

        buckets = np.array(buckets)
        buckets.sort()

        # assign clusters
        self.df.loc[:, 'cluster'] = buckets.searchsorted(self.df.score)

    def create_matrix(self):
        """
        Create matrix with tf-idf vectorizer
        """
        self.logger.info('Creating matrix from words')

        # create tf-idf vectorizer
        vectorizer = TfidfVectorizer()

        # apply vectorizer
        self.matrix = vectorizer.fit_transform(self.df['genres'])

    def recommend(self, movie_id):
        """
        Get recommended movies

        :param int movie_id: movie id for recommending
        :return: recommended movie ids
        :rtype: list
        """
        self.logger.info(f'Finding recommended films for id={movie_id}')

        # get index and cluster by selected movie
        index = self.df[self.df.title_id == movie_id].index[0]
        cluster = self.df[self.df.title_id == movie_id]['cluster'].iloc[0]
        kind = self.df[self.df.title_id == movie_id]['title_type'].iloc[0]

        # get similarity scores by genres
        kernel = linear_kernel(self.matrix[index], self.matrix)
        sim_scores = list(enumerate(kernel[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # select movies based on a similarity threshold of 0.5
        indexes = [i[0] for i in sim_scores if i[0] != index and i[1] > .5]

        cond1 = (self.df.index.isin(indexes))
        cond2 = (self.df.cluster == cluster)
        cond3 = (self.df.title_type == kind)

        args = {'by': 'score', 'ascending': False}
        selected = self.df.loc[cond1 & cond2 & cond3].sort_values(**args)

        return self.get_by_ids(selected['title_id'].tolist()[:12])
