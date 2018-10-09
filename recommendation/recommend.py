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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class Recommendation:
    def __init__(self):
        self.logger = logging.getLogger('Recommendation - Recommendation Class')

    def __preproccessing(self, text):
        """
        :param str text: text for preproccessing, description + genre
        :return: processed text
        :rtype: str
        """
        # self.logger.info('Text pre-processing is in progress...')
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
        # stems = [stem(word) for word in text.split(' ')]
        stems = [stem(word) for word in text.split(' ')]

        # removing stop words
        words = [w for w in stems if w not in default_stopwords]

        return ' '.join(map(str, words))

    def create_matrix(self, df):
        """
        :param dataframe df: dataframe for matrix creating
        :return: list of vectors
        :rtype: numpy.array
        """
        self.logger.info('Creating matrix from words...')
        tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000, min_df=0.2, use_idf=True,
                                           tokenizer=self.__preproccessing, ngram_range=(1, 3))

        matrix = tfidf_vectorizer.fit_transform(df['genre'] + df['description'])
        return linear_kernel(matrix, matrix)

    def recommend(self, movie_id, matrix):
        """
        :param int movie_id: movie id for recommending
        :param numpy.array matrix: list of vectors
        :return: recommended movie ids
        :rtype: list
        """
        self.logger.info('Finding recommended films for id={id}...'.format(id=movie_id))
        sim_scores = list(enumerate(matrix[movie_id - 1]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        movie_indices = [i[0] + 1 for i in sim_scores if (i[1] > 0.5) and (i[0] + 1 != movie_id)][0:30]
        return movie_indices


