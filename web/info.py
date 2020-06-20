from flask import Blueprint, render_template
from recommendation import rec, detection
from web import app

info = Blueprint('infocard', app.name)


@app.route('/infocard/<movie_id>')
def info_card(movie_id=None):
    """
    Get information card about series
    """
    movie = rec.get_by_ids(movie_id)
    episodes = movie.episode_ratings.split(',')
    information = movie.episode_info.split(',')

    ratings = list(map(float, episodes))
    cluster, message = detection.assign_cluster(ratings, information)

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
