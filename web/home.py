from util.elastic import Elastic
from flask import Blueprint, render_template, request
from recommendation import rec
from web import app

home = Blueprint('home', app.name)


@home.route('/suggest')
def suggest():
    """
    Suggestions for autocomplete
    """
    # get text from search form in home page
    es = Elastic()
    name = request.args.get('name')

    # search in elastic
    return es.search(name)


@home.route('/')
def index():
    """
    Get homepage
    """
    args = {
        'items': rec.get_by_n(),
        'active': 1
    }
    return render_template('index.html', **args)


@home.route('/lucky')
def lucky():
    """
    Get lucky page
    """
    # random choice by weights
    movie = rec.get_random()

    args = {
        'name': movie['original_title'],
        'image_url': movie['image_url'],
        'avg_rating': movie['average_rating'],
        'num_votes': movie['num_votes'],
        'genres': movie['genres'],
        'active': 2
    }
    return render_template('lucky.html', **args)


@home.route('/ping')
def ping():
    """
    System control
    """
    return 'pong'
