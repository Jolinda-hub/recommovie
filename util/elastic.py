from db.factory import BasicFactory
from elasticsearch import Elasticsearch, helpers, exceptions
from util import get_params, set_logger
import json

bf = BasicFactory()
config = get_params()
logger = set_logger('elastic')

es = Elasticsearch(hosts=[{
    'host': config['elastic']['host'],
    'port': config['elastic']['port']
}])


class Elastic:
    INDEX = config['elastic']['index']

    def search(self, name):
        """
        Autocomplete for movies

        :param str name: prefix from search
        :return: movies
        :rtype: dict
        """
        message = {'status': False}
        query = {
            'suggest': {
                'movie': {
                    'prefix': name,
                    'completion': {
                        'field': 'name',
                        'size': 10
                    }
                }
            }
        }
        # if status code is not equal to 200
        try:
            response = es.search(
                index=self.INDEX,
                body=query
            )
        except BaseException:
            return json.dumps(message)

        options = response['suggest']['movie'][0]['options']

        if response['timed_out'] or len(options) == 0:
            return json.dumps(message)

        # similar movie names and movies year
        movies = []

        for item in options:
            source = item['_source']
            data = {
                'id': item['_id'],
                'text': ' '.join(source['name']['input']),
                'value': source['year'],
            }
            movies.append(data)

        message['status'] = True
        message['movies'] = movies[:10]

        return json.dumps(message)

    def insert_elastic(self):
        """
        Insert records to elastic

        :return: difference between inserted and sent
        :rtype: int
        """
        items = bf.get_items()

        actions = []

        for item in items:
            action = {
                '_index': self.INDEX,
                '_id': item[0],
                '_source': {
                    'name': {
                        'input': item[1].split(),
                        'weight': int(item[3])
                    },
                    'year': item[2],
                },
            }
            actions.append(action)

        response = helpers.bulk(es, actions)
        warnings = len(items) - response[0]

        if warnings > 0:
            logger.warn(f'An error occurred for {warnings} items')

    @staticmethod
    def create_index():
        """
        Create index in elastic

        :return: status of request
        :rtype: bool
        """
        request_body = {
            'settings': {
                'number_of_shards': 3,
                'number_of_replicas': 1
            },
            'mappings': {
                'properties': {
                    'name': {
                        'type': 'completion',
                        'preserve_separators': False,
                        'preserve_position_increments': False
                    },
                    'year': {
                        'type': 'integer',
                        'index': False
                    }
                }
            }
        }

        try:
            es.indices.create(
                index=config['elastic']['index'],
                body=request_body
            )
        except exceptions.RequestError as e:
            if not e.args[1] == 'resource_already_exists_exception':
                logger.warn('Index already exists')
                return

            logger.exception(e.args)
