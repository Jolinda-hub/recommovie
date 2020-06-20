from flask import Blueprint, render_template
from pandas import isnull
from recommendation import rec
from web import app

rec_page = Blueprint('recommendations', app.name)


@rec_page.route('/<movie_id>')
def recommendations(movie_id=None):
    """
    Recommendations page
    """
    try:
        # movie features
        movie = rec.get_by_ids(movie_id)
        name = movie['original_title']

        args = {
            'header': 'Recommended movies for',
            'items': rec.recommend(movie_id),
            'original': name
        }
        return render_template('recommendations.html', **args)
    except BaseException:
        return render_template('error.html')
