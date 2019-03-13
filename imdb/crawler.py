# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from imdb.data import get_data
from db.data_opt import DataOperation
from util import Util
import concurrent.futures
import json
import pandas as pd
import requests

util = Util()
db = DataOperation()


class Crawler:
    def __init__(self):
        self.logger = util.set_logger('crawler')
        self.base_path = ' http://www.imdb.com/title/'

    def __get_page(self, movie_id):
        """
        Get page source

        :param str movie_id: movie id like tt0000001
        :return: http response
        :rtype: str
        """
        self.logger.info('Request being set...')
        full_path = self.base_path + movie_id
        resp = requests.get(full_path)
        return resp.text if resp.status_code == 200 else None

    def __parse(self, content):
        """
        Get image url and description

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

    def append(self, movie_id):
        """
        Create beautiful soup

        :param str movie_id: movie id like tt0000001
        :return: image and description
        :rtype: tuple
        """
        resp = self.__get_page(movie_id)
        soup = BeautifulSoup(resp, 'html.parser')

        img, description = self.__parse(soup)

        return img, description

    def edit(self, df):
        """
        Map columns for db insert

        :param dataframe df: dataframe for renaming columns
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
        renamed = replaced.rename(columns=column_maps)
        return renamed

    def crawl(self):
        """
        Crawl movies description and image url

        :return: error count from movies crawler
        :rtype: int
        """
        df = get_data()

        records = []
        future_to_id = {}
        errors = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            for movie_id in df['tconst'].unique():
                submission = executor.submit(self.append, movie_id)
                future_to_id[submission] = movie_id

            for future in concurrent.futures.as_completed(future_to_id):
                movie_id = future_to_id[future]
                try:
                    data = future.result()
                except Exception as exc:
                    self.logger.error('%r generated an exception: %s' % (movie_id, exc))
                    errors += 1
                else:
                    records.append(data + (movie_id,))

        df_img = pd.DataFrame(records, columns=['image_url', 'description', 'tconst'])
        df_all = df_img.merge(df, on='tconst')

        df_last = self.edit(df_all)
        db.insert(df_last)

        return errors
