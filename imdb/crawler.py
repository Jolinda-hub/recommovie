# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from db_connection import DbConnection
from models import Movie
import logging
import math
import numpy as np
import re
import requests
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)


class Crawler:
    def __init__(self):
        self.logger = logging.getLogger('IMDB - Crawler Class')

    def __get_page(self, year, rating, start=1):
        """
        :param int year: year of movies
        :param float rating: first element of rating range -> (1.0, 1.7)
        :return: response from request
        :rtype: requests.models.Response
        """
        self.logger.info('Request being set...')

        # Rating between 1 and 1.5 in first case
        # And after, (1.6, 2.0), (2.1, 2.4) etc.
        lower_bound = rating + 0.1 if rating != 1 else rating
        upper_bound = rating + 0.5
        rating_str = '{0},{1}'.format(lower_bound, upper_bound)

        # "404 page not found" error returns after 10000 movies
        resp = requests.get(
            'https://www.imdb.com/search/title?user_rating={r}&year={y}&start={s}'.format(r=rating_str, y=year,
                                                                                          s=start))
        return resp if resp.status_code == 200 else None

    def __get_movie_count(self, year, rating):
        """
        :param int year: year of movies
        :param float rating: first element of rating range -> (1.0, 1.7)
        :return: page number for request
        :rtype: float or int
        """
        # If the number of pages is more than one, look at other pages
        # Return the result to avoid requesting the first page again
        resp = self.__get_page(year, rating)

        if resp is not None:
            self.logger.info('Request turned 200!')
            soup = BeautifulSoup(resp.text, 'html.parser')
            span = soup.findAll('div', attrs={'class': 'desc'})
            span = [s.text for s in span]

            if len(span) > 0:
                spans = re.findall('\d+', str(span[0]))
                spans = sorted([int(element) for element in spans], reverse=True)
                if len(spans) > 0:
                    return math.ceil(float(spans[0]) / 50), resp
                else:
                    return 0, resp
            else:
                return 0, resp
        else:
            return 0, resp

    def __get_movie_name(self, content):
        """
        :param bs4.element.Tag content: contains div elements
        :return: movie name
        :rtype: str
        """
        self.logger.info('Fetching movie name...')
        header = content.findNext('h3', attrs={'class': 'lister-item-header'})
        return str(header.findNext('a').text).encode('ascii', 'ignore').decode('ascii')

    def __get_genre(self, content):
        """
        :param bs4.element.Tag content: contains div elements
        :return: genre of movie, action, romantic etc.
        :rtype: str
        """
        self.logger.info('Fetching genre of movie...')
        span = content.findNext('span', attrs={'class': 'genre'})
        return re.sub(r'[\n\r]+', '', span.text).lower() if span is not None else None

    def __get_imdb_rating(self, content):
        """
        :param bs4.element.Tag content: contains div elements
        :return: imdb rating of movie
        :rtype: float
        """
        self.logger.info('Fetching IMDB rating of movie...')
        span = content.findNext('span', attrs={'class': 'global-sprite rating-star imdb-rating'})
        if span is not None:
            strong = span.findNext('strong')
            return float(strong.text)
        else:
            return None

    def __get_movie_kind(self, content):
        """
        :param str content: contains year of movie
        :return: kind of movie
        :rtype: str
        """
        # Movie -> 1, Series -> 0
        self.logger.info('Fetching kind of movie...')
        if '–' in content:
            return 0
        else:
            return 1

    def __get_movie_year(self, content):
        """
        :param bs4.element.Tag content: contains div elements
        :return: kind and year of movie
        :rtype: str
        """
        self.logger.info('Fetching year of movie...')
        span = content.findNext('span', attrs={'class': 'lister-item-year text-muted unbold'})
        kind = self.__get_movie_kind(span.text)
        cond1 = span.text is not None
        cond2 = span.text != ''
        cond3 = len(re.findall('\d+', span.text)) > 0
        year = re.findall('\d+', span.text)[0] if cond1 and cond2 and cond3 else 0
        return kind, int(year)

    def __get_movie_description(self, content):
        """
        :param bs4.element.Tag content: contains div elements
        :return: description of movie
        :rtype: str
        """
        self.logger.info('Fetching description of movie...')

        if content is not None:
            p = content.findAll('p', attrs={'class': 'text-muted'})[1]
            description = re.sub(r'[\n\r]+', '', p.text).lower()
            return str(description).encode('ascii', 'ignore').decode('ascii')
        else:
            return None

    def __parse_html(self, year=None, rating=None, page=None, resp=None):
        """
        :param int year: year of movies
        :param float rating: first element of rating range -> (1.0, 1.7)
        :return: movie parameters name, id etc.
        :rtype: list
        """
        resp = self.__get_page(year, rating, page) if resp is None else resp
        soup = BeautifulSoup(resp.text, 'html.parser')
        records = list()

        for content in soup.findAll('div', attrs={'class': 'lister-item-content'}):
            movie_name = self.__get_movie_name(content)
            genre = self.__get_genre(content)
            rating = self.__get_imdb_rating(content)
            kind, year = self.__get_movie_year(content)
            description = self.__get_movie_description(content)
            record = Movie(name=movie_name, genre=genre, rating=rating, kind=kind, year=year, description=description)
            records.append(record)
        return records

    def append(self):
        db = DbConnection()

        # You can change the start year
        for year in range(1900, 2019, 1):
            for rating in np.arange(1, 10, 0.5):
                page, resp = self.__get_movie_count(year, rating)
                db.insert(self.__parse_html(resp=resp))
                if page <= 1:
                    pass
                else:
                    for i in range(1, int(page), 1):
                        records = self.__parse_html(year, rating, (i * 50) + 1)
                        db.insert(records)
