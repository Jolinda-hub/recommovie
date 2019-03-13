from web.app import app
from util.elastic import Elastic
from util import Util


def main():
    util = Util()
    elastic = Elastic()

    # get config and set logger
    config = util.get_params()
    logger = util.set_logger('main')

    # create index in elastic search
    resp = elastic.create_index()

    # check that it was created
    if resp:
        logger.info('Index created successfully!')
    else:
        logger.error('Error occurred in creating index!')

    # insert records to elasticsearch
    diff = elastic.insert_elastic()

    # check that it was inserted
    if diff == 0:
        logger.info('Movies inserted successfully to elasticsearch!')
    else:
        logger.error(f'Elasticsearch: Error occurred in {diff} movies!')

    # run web app
    app.run(port=5002, debug=config['app'].getboolean('debug'))


if __name__ == '__main__':
    main()
