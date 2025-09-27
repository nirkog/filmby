from flask import Blueprint

bp = Blueprint('show_events', __name__)

from server.show_events import routes
