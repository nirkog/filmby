from flask import Flask

from server.index import bp as index_bp
from server.show_films import bp as show_films_bp
import server.films as films

UPDATE_INTERVAL_IN_MINUTES = 60
UPDATE_INTERVAL_IN_SECONDS = UPDATE_INTERVAL_IN_MINUTES * 60

def create_app(test_config=None):
    # app = Flask(__name__, template_folder=os.path.abspath("./templates/"), static_folder=os.path.abspath("./static/"))
    app = Flask(__name__)

    app.register_blueprint(index_bp)
    app.register_blueprint(show_films_bp)

    films.start_film_updating_thread(UPDATE_INTERVAL_IN_SECONDS)

    app.config["TEMPLATES_AUTO_RELOAD"] = True

    return app
