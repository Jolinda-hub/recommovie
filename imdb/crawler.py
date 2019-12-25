from bs4 import BeautifulSoup
from db.data_opt import DataOperation
from imdb.data import get_data
from util import Util
import json
import multiprocessing as mp
import pandas as pd
import requests
import time
import tqdm

util = Util()
db = DataOperation()

logger = util.set_logger('crawler')
BASE_PATH = ' http://www.imdb.com/title/'


def get_page(movie_id):
    """
    Get page source

    :param str movie_id: movie id like tt0000001
    :return: http response
    :rtype: str
    """
    full_path = BASE_PATH + movie_id
    resp = requests.get(full_path)
    return resp.text if resp.status_code == 200 else None


def parse(content):
    """
    Get image url, description and trailer id

    :param bs4.BeautifulSoup content: BeautifulSoup from html content
    :return: image, description and trailer id
    :rtype: tuple
    """
    img = description = trailer_id = None

    attrs = {'type': 'application/ld+json'}
    full_info = content.find('script', attrs=attrs).text
    info_dict = json.loads(full_info)

    if 'image' in info_dict.keys():
        img = info_dict['image']
    if 'description' in info_dict.keys():
        description = info_dict['description']
    if 'trailer' in info_dict.keys():
        trailer_id = info_dict['trailer']['embedUrl'].split('/')[3]

    return img, description, trailer_id


def append(movie_id):
    """
    Create beautiful soup

    :param str movie_id: movie id like tt0000001
    :return: image, description and trailer id
    :rtype: tuple
    """
    img = description = trailer_id = None

    try:
        resp = get_page(movie_id)
        soup = BeautifulSoup(resp, 'html.parser')
        img, description, trailer_id = parse(soup)
    except Exception as e:
        logger.error(f'An error occurred: {e.args} for movie_id={movie_id}')
        time.sleep(10)

    return movie_id, img, description, trailer_id


def edit(df):
    """
    Map columns for db insert

    :param pd.DataFrame df: dataframe for renaming columns
    :return: renamed-decoded data frame
    :rtype: pd.DataFrame
    """
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


def crawl(args):
    """
    Crawl movies description and image url

    :param dict args: arguments
    :return: movies
    :rtype: pd.DataFrame
    """
    movies = get_data(n=args['c'])
    old_ids = db.get_movie_ids()

    df = movies[~movies.tconst.isin(old_ids)]

    pool = mp.Pool(args['w'])
    ids = df['tconst'].unique()

    records = list(tqdm.tqdm(pool.imap(append, ids), total=len(ids)))
    pool.close()
    pool.join()

    columns = ['tconst', 'image_url', 'description', 'trailer_id']
    df_img = pd.DataFrame(records, columns=columns)
    df_all = df_img.merge(df, on='tconst')

    return edit(df_all)
