from flask import Blueprint, render_template
from web import app

policy = Blueprint('policy', app.name)


@policy.route('/terms_and_conditions')
def terms_and_conditions():
    """
    Terms and conditions
    """
    return render_template('terms_and_conditions.html')


@policy.route('/privacy_policy')
def privacy_policy():
    """
    Privacy policy
    """
    return render_template('privacy_policy.html')
