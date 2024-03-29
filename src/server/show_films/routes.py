import datetime
import json
from flask import render_template, request
from loguru import logger

from server.show_films import bp
from server.films import film_manager

def filter_films(date, town):
    films = []
    indices = []
    for i, film in enumerate(film_manager.films):
        if town in film.dates:
            if date != None:
                if not film.has_screenings_on_date(date):
                    continue
            films.append(film)
            indices.append(i)

    return indices, films

@bp.route('/films')
def show_films():
    date = None
    if "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
    indices, filtered_films = filter_films(date, request.args["town"])
    logger.debug(f"Found {len(filtered_films)} relevant films")

    if "json" in request.args:
        if bool(request.args["json"]):
            result = [film.json_serializable() for film in filtered_films]
            for i, film in enumerate(result):
                film["index"] = indices[i]
            return json.dumps(result)

    return render_template('films.html', films=filtered_films, indices=indices)
