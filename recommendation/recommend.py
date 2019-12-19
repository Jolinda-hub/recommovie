# -*- coding: utf-8 -*-
from scipy.signal import argrelextrema
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors.kde import KernelDensity
from sklearn.preprocessing import LabelEncoder
from util import Util
import numpy as np

util = Util()
config = util.get_params()


class Recommendation:
    def __init__(self, df):
        self.logger = util.set_logger('recommendation')
        self.matrix = None
        self.df = df

        self.preproccessing()
        self.clustering()
        self.create_matrix()

    def preproccessing(self):
        """
        Data pre-processing
        """
        le = LabelEncoder()

        self.df.loc[:, 'kind'] = le.fit_transform(self.df['kind'])

        self.df.loc[:, 'score'] = (
                float(config['score']['num_votes']) * self.df['num_votes'] +
                float(config['score']['runtime']) * self.df['runtime'] +
                float(config['score']['year']) * self.df['start_year'] +
                float(config['score']['kind']) * self.df['kind']
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
        s = np.linspace(400, 18000)
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

        :return: list of vectors
        :rtype: numpy.array
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
        index = self.df[self.df.movie_id == movie_id].index[0]
        cluster = self.df[self.df.movie_id == movie_id]['cluster'].iloc[0]
        kind = self.df[self.df.movie_id == movie_id]['kind'].iloc[0]

        # get similarity scores by genres
        kernel = linear_kernel(self.matrix[index], self.matrix)
        sim_scores = list(enumerate(kernel[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # select movies based on a similarity threshold of 0.5
        indexes = [i[0] for i in sim_scores if i[0] != index and i[1] > .5]

        cond1 = (self.df.index.isin(indexes))
        cond2 = (self.df.cluster == cluster)
        cond3 = (self.df.kind == kind)

        args = {'by': 'score', 'ascending': False}
        selected = self.df.loc[cond1 & cond2 & cond3].sort_values(**args)

        return selected['movie_id'].tolist()[:12]
