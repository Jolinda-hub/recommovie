from web import app
from web.home import home
from web.info import info
from web.rec import rec_page
from web.user import auth
from util.elastic import Elastic
from util import get_params


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
    app.register_blueprint(auth, url_prefix='/user')

    # run web app
    port = config['app'].getint('port')
    debug = config['app'].getboolean('debug')
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
