# -*- coding: utf-8 -*-
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from stemming.porter2 import stem
import logging
import nltk
import re
import string

nltk.download('punkt')
nltk.download('stopwords')
default_stopwords = stopwords.words('english')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)


class Recommendation:
    def __init__(self, df):
        self.logger = logging.getLogger('Recommendation - Recommendation Class')
        self.map_dict = self.mapping(df)
        self.matrix = self.create_matrix(df)

    def __preproccessing(self, text):
        """
        :param str text: text for preproccessing, description + genre
        :return: processed text
        :rtype: str
        """
        self.logger.info('Text pre-processing is in progress...')

        # remove html tags
        text = re.sub(r'<.*?>', '', text)

        # remove the characters [\], ['] and ["]
        text = re.sub(r"\\", "", text)
        text = re.sub(r"\'", "", text)
        text = re.sub(r"\"", "", text)
        text = re.sub(r"\d+", "", text)

        # convert text to lowercase
        text = text.strip().lower()

        # replace punctuation characters with spaces
        replace_punctuation = string.maketrans(string.punctuation, ' ' * len(string.punctuation))
        text = str(text).translate(replace_punctuation)

        # stemming (removing ed, es etc.)
        stems = [stem(word) for word in text.split(' ')]

        # removing stop words
        words = [w for w in stems if w not in default_stopwords]

        return ' '.join(map(str, words))

    def mapping(self, df):
        self.logger.info('Mapping between fake id and original id...')

        df['fake_id'] = range(1, len(df) + 1)
        map_dict = dict()
        for idx, fake_id in zip(df['movie_id'].tolist(), df['fake_id'].tolist()):
            map_dict[fake_id] = idx

        return map_dict

    def create_matrix(self, df):
        """
        :param dataframe df: dataframe for matrix creating
        :return: list of vectors
        :rtype: numpy.array
        """
        self.logger.info('Creating matrix from words...')

        args = {
            'max_df': 0.8,
            'max_features': 200000,
            'min_df': 0.2,
            'use_idf': True,
            'tokenizer': self.__preproccessing,
            'ngram_range': (1, 3),
        }

        # create tf-idf vectorizer
        tfidf_vectorizer = TfidfVectorizer(**args)

        # encode ascii chars
        df['description'] = df['description'].apply(lambda x: x.encode('ascii', 'ignore').decode('ascii'))

        # apply vectorizer
        matrix = tfidf_vectorizer.fit_transform(df['genres'] + df['description'])
        return matrix

    def recommend(self, movie_id):
        """
        :param int movie_id: movie id for recommending
        :return: recommended movie ids
        :rtype: list
        """
        self.logger.info('Finding recommended films for id={id}...'.format(id=movie_id))

        # get fake id from original movie id
        fake_id = self.map_dict.keys()[self.map_dict.values().index(str(movie_id))]

        # create kernel for cosine similarity
        kernel = linear_kernel(self.matrix[fake_id - 1], self.matrix)
        sim_scores = list(enumerate(kernel[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # return original movie ids
        movie_indices = [i[0] + 1 for i in sim_scores if (i[1] > 0.5) and (i[0] + 1 != fake_id)][0:50]
        return [str(v) for k, v in self.map_dict.items() if k in movie_indices]
