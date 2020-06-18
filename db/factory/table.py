from db import connect
from db.model import Basic, Episode, Rating


class TableFactory:
    def __init__(self):
        self.mapping = {
            'basics': Basic,
            'episodes': Episode,
            'ratings': Rating
        }

    def get_by_table_name(self, name):
        """
        Get movie ids by table name

        :param str name: table name
        :return: movie ids
        :rtype: list
        """
        session = connect()
        table = self.mapping[name]
        query = session.query(table.title_id)

        try:
            return [r[0] for r in query.all()]
        finally:
            session.close()
