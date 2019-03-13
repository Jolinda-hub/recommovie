from db.data_opt import DataOperation
from elasticsearch import Elasticsearch, helpers, exceptions
from util import Util

util = Util()
db = DataOperation()

config = util.get_params()
es = Elasticsearch(hosts=[{'host': config['elastic']['host'], 'port': config['elastic']['port']}])


class Elastic:
    @staticmethod
    def insert_elastic():
        """
        Insert records to elasticsearch

        :return: difference between inserted and sent
        :rtype: int
        """
        items = db.get_items()

        actions = []

        for item in items:
            action = {
                '_index': 'movies',
                '_type': 'movies',
                '_id': item[0],
                '_source': {
                    'name': item[1],
                    'year': item[2],
                },
            }
            actions.append(action)

        response = helpers.bulk(es, actions)
        return len(items) - response[0]

    @staticmethod
    def create_index():
        """
        Create index in elasticsearch

        :return: status of request
        :rtype: bool
        """
        request_body = {
            'setting': {
                'number_of_shards': 3,
                'number_of_replicas': 1,
            },
            'mappings': {
                'movies': {
                    'properties': {
                        'name': {
                            'type': 'completion',
                            'preserve_separators': False,
                            'preserve_position_increments': False,
                        },
                        'year': {
                            'type': 'keyword',
                        }
                    }
                }
            }
        }
        status = False

        try:
            es.indices.create(index='movies', body=request_body)
            status = True
        except exceptions.RequestError as e:
            if e.args[1] == 'resource_already_exists_exception':
                status = True
            else:
                status = False
        finally:
            return status
