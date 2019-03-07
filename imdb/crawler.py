# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import logging
import requests
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)


class Crawler:
    def __init__(self):
        self.logger = logging.getLogger('IMDB - Crawler Class')
        self.base_path = ' http://www.imdb.com/title/'

    def __get_page(self, movie_id):
        """
        :param str movie_id: movie id like tt0000001
        :return: http response
        :rtype: str
        """
        self.logger.info('Request being set...')
        full_path = self.base_path + movie_id
        resp = requests.get(full_path)
        return resp if resp.status_code == 200 else None

    def __parse(self, content):
        """
        :param bs4.BeautifulSoup content: BeautifulSoup from html content
        :return: image and description
        :rtype: tuple
        """
        self.logger.info('Parsing ld json...')
        img = None
        description = None

        full_info = content.find('script', attrs={'type': 'application/ld+json'}).text
        info_dict = json.loads(full_info)

        if 'image' in info_dict.keys():
            img = info_dict['image']
        if 'description' in info_dict.keys():
            description = info_dict['description']

        return img, description

    def append(self, movie_id, name, year):
        """
        :param str movie_id: movie id like tt0000001
        :param str name: movie name
        :param int year: movie year
        :return: image and description
        :rtype: tuple
        """
        resp = self.__get_page(movie_id)
        soup = BeautifulSoup(resp.text, 'html.parser')

        img, description = self.__parse(soup)

        # elastic_data = {'name': name, 'year': year}
        # resp = requests.post('http://localhost:9200/movies/movies/' + str(movie_id), json=elastic_data)
        #
        # if resp.status_code not in [200, 201]:
        #     self.logger.error('Error in request: ' + resp.text)
        # else:
        #     self.logger.info('Request sent successfully!')

        return img, description

    def edit(self, df):
        """
        :param dataframe df: dataframe for renaming columns and decode with utf8
        :return: renamed-decoded dataframe
        :rtype: dataframe
        """
        self.logger.info('Editing last dataframe...')

        column_maps = {
            'tconst': 'movie_id',
            'titleType': 'kind',
            'primaryTitle': 'primary_title',
            'originalTitle': 'title',
            'isAdult': 'is_adult',
            'startYear': 'start_year',
            'endYear': 'end_year',
            'runtimeMinutes': 'runtime',
            'averageRating': 'average_rating',
            'numVotes': 'num_votes',
        }

        replaced = df.replace('\\N', '')

        for col in ['description', 'titleType', 'primaryTitle', 'originalTitle']:
            try:
                replaced[col] = replaced[col].apply(lambda x: x.decode('utf-8') if x is not None else None)
            except Exception as e:
                self.logger.error(e.args)

        renamed = replaced.rename(columns=column_maps)
        return renamed
