from flask import Blueprint

bp = Blueprint('index', __name__)

from server.index import routes
