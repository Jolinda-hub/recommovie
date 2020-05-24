from flask import Flask, request, render_template, send_from_directory, jsonify
from db.factory import Factory
from recommendation.recommend import Recommendation
from recommendation.trend import TrendDetection
from util import get_params
import pandas as pd
import random
import requests

config = get_params()
factory = Factory()
detection = TrendDetection()

app = Flask(__name__)
app.secret_key = config['app']['secret']

movie_df = factory.get_dataframe()
episode_df = factory.get_episodes()

merged = movie_df.merge(episode_df, on='title_id', how='left')
recommend = Recommendation(merged)


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


@app.route('/recommendations/<movie_id>', methods=['GET'])
def recommendations(movie_id=None):
    try:
        # movie features
        movie = merged[merged.title_id == movie_id].iloc[0]
        name = movie['original_title']
        ratings = movie['episode_ratings']
        flag = False if pd.isnull(ratings) else True

        # recommendations
        movie_ids = recommend.recommend(movie_id)
        items = movie_df[movie_df.title_id.isin(movie_ids)].itertuples()

        args = {
            'items': items,
            'original': name,
            'flag': flag
        }
        return render_template('recommendations.html', **args)
    except:
        return render_template('error.html')


@app.route('/lucky', methods=['GET'])
def lucky():
    # random choice by weights
    filtered = merged[merged.image_url.notnull()]
    title_id = random.choices(
        filtered.title_id.tolist(),
        filtered.num_votes.tolist()
    )[0]
    movie = filtered[filtered.title_id == title_id].iloc[0]

    args = {
        'name': movie['original_title'],
        'image_url': movie['image_url'],
        'avg_rating': movie['average_rating'],
        'num_votes': movie['num_votes'],
        'genres': movie['genres'],
        'active': 2
    }
    return render_template('lucky.html', **args)


@app.route('/infocard/<movie_id>', methods=['GET'])
def info_card(movie_id=None):
    condition = merged.title_id == movie_id
    movie = merged[condition].iloc[0]

    episodes = movie.episode_ratings.split(',')
    info = movie.episode_info.split(',')

    ratings = list(map(float, episodes))
    cluster, message = detection.assign_cluster(ratings, info)

    args = {
        'name': movie.original_title,
        'image_url': movie.image_url,
        'min': min(ratings),
        'max': max(ratings),
        'avg': round(sum(ratings) / len(ratings), 1),
        'trend': cluster.replace('_', ' ').title(),
        'message': message.capitalize()
    }

    return render_template('infocard.html', **args)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'
