from flask import Flask, request, render_template, send_from_directory, jsonify
from db.data_opt import DataOperation
from recommendation.recommend import Recommendation
from util import Util
import requests

db = DataOperation()
util = Util()
config = util.get_params()

app = Flask(__name__)
app.secret_key = config['app']['secret']

movie_df = db.get_dataframe()
recommend = Recommendation(movie_df)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/img/<path:path>')
def send_images(path):
    return send_from_directory('static/img', path)


@app.route('/', methods=['GET'])
def index():
    args = {
        'items': movie_df.head(8).itertuples(),
        'active': 1,
    }
    return render_template('index.html', **args)


@app.route('/suggest', methods=['GET'])
def suggest():
    movie_id = request.args['movie_id']

    response = {'status': False}

    # set query for elastic
    query = {
        'suggest': {
            'movie': {
                'prefix': movie_id,
                'completion': {
                    'field': 'name',
                    'size': 10
                }
            }
        }
    }

    # get elastic host, port, index and type
    host = config['elastic']['host']
    port = config['elastic']['port']
    index_ = config['elastic']['index']
    type_ = config['elastic']['type']

    # request to elastic
    args = {
        'url': f'http://{host}:{port}/{index_}/{type_}/_search',
        'json': query,
    }
    res = requests.post(**args)
    if res.status_code != 200:
        return jsonify(response)

    # get similar options
    data = res.json()
    options = data['suggest']['movie'][0]['options']

    # timeout control
    if data['timed_out'] or len(options) == 0:
        return jsonify(response)

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

    response = {
        'status': True,
        'movies': movies[:10]
    }

    return jsonify(response)


@app.route('/recommendations/<movie_id>/<name>', methods=['GET'])
def recommendations(movie_id=None, name=None):
    try:
        movie_ids = recommend.recommend(movie_id)
        items = movie_df[movie_df.movie_id.isin(movie_ids)].itertuples()

        args = {
            'items': items,
            'original': name,
        }
        return render_template('recommendations.html', **args)
    except:
        return render_template('error.html')


@app.route('/lucky', methods=['GET'])
def lucky():
    movie = movie_df.sample(1).iloc[0]
    movie_ids = recommend.recommend(movie.movie_id)
    items = movie_df[movie_df.movie_id.isin(movie_ids)].itertuples()

    args = {
        'items': items,
        'original': movie.title,
        'active': 2,
    }
    return render_template('recommendations.html', **args)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'
