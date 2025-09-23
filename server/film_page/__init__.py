from flask import Blueprint

bp = Blueprint('film_page', __name__)

from server.film_page import routes
