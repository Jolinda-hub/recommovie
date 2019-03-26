from flask import Flask, request, render_template, send_from_directory, jsonify
from db.data_opt import DataOperation
from recommendation.recommend import Recommendation
from util import Util
import requests

app = Flask(__name__, static_url_path='')
app.secret_key = 'super secret key'

db = DataOperation()
util = Util()

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
    res = db.get_movies()
    return render_template('index.html', items=res)


@app.route('/suggest', methods=['GET'])
def suggest():
    movie_id = request.args['movie_id']

    response = {'status': False}

    # set query for elasticsearch
    query = {
        'suggest': {
            'movie': {
                'prefix': movie_id,
                'completion': {
                    'field': 'name'
                }
            }
        }
    }

    # get elastic host and port
    config = util.get_params()
    host = config['elastic']['host']
    port = config['elastic']['port']

    # request to elasticsearch
    res = requests.post(f"http://{host}:{port}/movies/movies/_search", json=query)
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
        movies.append({'id': item['_id'], 'text': source['name'], 'value': source['year']})

    response = {
        'status': True,
        'movies': movies[0:3]
    }

    return jsonify(response)


@app.route('/recommendations/<movie_id>/<name>', methods=['GET'])
def recommendations(movie_id=None, name=None):
    movie_ids = recommend.recommend(movie_id)
    res = db.get_movies(movie_ids=movie_ids)
    return render_template('recommendations.html', items=res, original=name)
