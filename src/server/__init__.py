import sys
import os

from loguru import logger
from flask import Flask, g

from server.index import bp as index_bp
from server.show_films import bp as show_films_bp
from server.film_page import bp as film_page_bp
from server.films import FilmManager, film_manager

UPDATE_INTERVAL_IN_HOURS = 4
UPDATE_INTERVAL_IN_SECONDS = UPDATE_INTERVAL_IN_HOURS * 60 * 60

CONSOLE_LOG_FORMAT = "<green>[{time:HH:mm:ss}]</green> | <lvl>{level}</lvl> | {file} | {message}"
FILE_LOG_FORMAT = "<green>[{time:DD-MM-YY HH:mm:ss}]</green> | <lvl>{level}</lvl> | {file} | {function} | {message}"

def create_app(test_config=None):
    # app = Flask(__name__, template_folder=os.path.abspath("./templates/"), static_folder=os.path.abspath("./static/"))
    app = Flask(__name__)

    ignore_cache = False
    if "IGNORE_CACHE" in os.environ:
        ignore_cache = bool(os.environ["IGNORE_CACHE"])

    logger.remove()
    if app.debug:
        logger.add(sys.stdout, format=CONSOLE_LOG_FORMAT, level="DEBUG")
        logger.add("filmby.log", format=FILE_LOG_FORMAT, level="DEBUG")
    else:
        logger.add(sys.stdout, format=CONSOLE_LOG_FORMAT, level="INFO")
        logger.add("filmby.log", format=FILE_LOG_FORMAT, level="INFO")

    app.register_blueprint(index_bp)
    app.register_blueprint(show_films_bp)
    app.register_blueprint(film_page_bp)

    if ignore_cache:
        logger.info("Ignoring cache")

    film_manager.start_film_updating_at_interval(UPDATE_INTERVAL_IN_SECONDS, ignore_cache=ignore_cache)

    app.config["TEMPLATES_AUTO_RELOAD"] = True

    return app
