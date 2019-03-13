from imdb.crawler import Crawler
from util import Util


def main():
    crawler = Crawler()
    util = Util()
    logger = util.set_logger('main')

    # crawl movies
    errors = crawler.crawl()

    # check error count from crawler
    if errors == 0:
        logger.info('Crawler done successfully!')
    else:
        logger.error(f'Crawler: Error occurred in {errors} movies!')


if __name__ == '__main__':
    main()
