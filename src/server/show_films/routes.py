import datetime
import json
from flask import render_template, request
from loguru import logger

from server.show_films import bp
from server.films import film_manager

# TODO: This is a patch, fix this
FILM_NAME_TRANSLATIONS = {
        "Canada": "קולנוע קנדה",
        "Cinema City": "סינמה סיטי",
        "Cinematheque": "סינמטק",
        "Jaffa": "קולנוע יפו",
        "Lev": "קולנוע לב",
        "Rav Hen": "רב חן"
}

DAY_NAMES = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]

def get_day_name(date):
    try:
        return DAY_NAMES[date.weekday()]
    except Exception:
        return ""

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

def get_day_name(date):
    try:
        return DAY_NAMES[date.weekday()]
    except Exception:
        return ""

def filter_dates(dates, chosen_date):
    filtered = []
    for date in dates:
        if date.day == chosen_date.day and date.month == chosen_date.month and date.year == chosen_date.year:
            filtered.append(date)
    
    return filtered

@bp.route('/films')
def show_films():
    date = None
    if "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
    indices, filtered_films = filter_films(date, request.args["town"])
    logger.debug(f"Found {len(filtered_films)} relevant films")

    logger.info(f"PAGE REQUEST /films - date {date}")

    if "json" in request.args:
        if bool(request.args["json"]):
            result = [film.json_serializable() for film in filtered_films]
            for i, film in enumerate(result):
                film["index"] = indices[i]
            return json.dumps(result)

    # screenings = get_screenings(filtered_films, date)

    return render_template(
            'films.html',
            films=filtered_films,
            indices=indices,
            town="Tel Aviv",
            date=date,
            name_translations=FILM_NAME_TRANSLATIONS,
            get_day_name=get_day_name,
            filter_dates=filter_dates)
