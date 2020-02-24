from crawl import main as crawl
from util import Util
from util.elastic import Elastic
import os
import wget

BASICS = 'https://datasets.imdbws.com/title.basics.tsv.gz'
RATINGS = 'https://datasets.imdbws.com/title.ratings.tsv.gz'


def main():
    util = Util()
    elastic = Elastic()
    config = util.get_params()
    path = config['crawler']['path']

    # download imdb files
    wget.download(BASICS, out=path)
    wget.download(RATINGS, out=path)

    # crawl movies and add to elastic
    crawl()
    _ = elastic.insert_elastic()

    # remove files
    os.remove(f"{config['crawler']['path']}/title.basics.tsv.gz")
    os.remove(f"{config['crawler']['path']}/title.ratings.tsv.gz")


if __name__ == '__main__':
    main()
