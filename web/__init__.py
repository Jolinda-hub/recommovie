from flask import Flask
from util import get_params

config = get_params()
app = Flask(
    'recommovie',
    template_folder='template',
    static_url_path='/static'
)
app.secret_key = config['app']['secret']
