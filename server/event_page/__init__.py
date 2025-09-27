from flask import Blueprint

bp = Blueprint('event_page', __name__)

from server.event_page import routes
