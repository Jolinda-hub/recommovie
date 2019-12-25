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
    msg = elastic.create_index()

    # check that it was created
    if msg is None:
        logger.info('Index created successfully!')
    else:
        logger.error(f'Error occurred in creating index:\n {msg}')

    # insert records to elastic
    diff = elastic.insert_elastic()

    # check that it was inserted
    if diff == 0:
        logger.info('Movies inserted successfully to elastic!')
    else:
        logger.error(f'Elastic: Error occurred in {diff} movies!')

    # run web app
    app.run(host='0.0.0.0', port=5002, debug=config['app'].getboolean('debug'))


if __name__ == '__main__':
    main()
