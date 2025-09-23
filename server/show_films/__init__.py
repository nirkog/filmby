from flask import Blueprint

bp = Blueprint('show_films', __name__)

from server.show_films import routes
