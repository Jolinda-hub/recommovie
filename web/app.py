from flask import Flask, request, render_template, redirect, send_from_directory, url_for, jsonify
import os
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from imdb.db_connection import DbConnection
from recommendation.recommend import Recommendation

app = Flask(__name__, static_url_path='')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = DbConnection()

movie_df = db.get_dataframe()
recommend = Recommendation(movie_df)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/vendor/<path:path>')
def send_js(path):
    return send_from_directory('static/vendor', path)


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

    res = requests.post('http://localhost:9200/movies/movies/_search', json=query)
    if res.status_code != 200:
        return jsonify(response)

    data = res.json()
    options = data['suggest']['movie'][0]['options']

    if data['timed_out'] or len(options) == 0:
        return jsonify(response)

    movies = []
    for item in options:
        source = item['_source']
        movies.append({'id': item['_id'], 'text': source['name'], 'value': source['year']})

    response = {
        'status': True,
        'movies': movies[0:3]
    }

    return jsonify(response)


@app.route('/recommendations/<movie_id>', methods=['GET'])
def location(movie_id=None):
    return str(recommend.recommend(movie_id))


if __name__ == '__main__':
    app.run(port=5002, debug=True)
