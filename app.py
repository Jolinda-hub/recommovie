from web import app
from web.home import home
from web.info import info
from web.rec import rec_page
from util.elastic import Elastic
from util import *


def main():
    elastic = Elastic()
    config = get_params()

    # create index and insert
    elastic.create_index()
    elastic.insert_elastic()

    # register
    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(rec_page, url_prefix='/recommendations')
    app.register_blueprint(info, url_prefix='/infocard')

    # run web app
    port = config['app'].getint('port')
    debug = config['app'].getboolean('debug')
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
