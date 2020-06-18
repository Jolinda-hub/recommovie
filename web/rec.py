from flask import Blueprint, render_template
from pandas import isnull
from recommendation import rec
from web import app

rec_page = Blueprint('recommendations', app.name)


@rec_page.route('/<movie_id>', methods=['GET'])
def recommendations(movie_id=None):
    """
    Recommendations page
    """
    try:
        # movie features
        movie = rec.get_by_ids(movie_id)
        name = movie['original_title']
        ratings = movie['episode_ratings']
        flag = False if isnull(ratings) else True

        args = {
            'items': rec.recommend(movie_id),
            'original': name,
            'flag': flag
        }
        return render_template('recommendations.html', **args)
    except BaseException:
        return render_template('error.html')
