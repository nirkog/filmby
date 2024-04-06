import datetime
from flask import render_template, request, redirect
from loguru import logger

from server.film_page import bp
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

@bp.route('/film/<film_index>')
def film_page(film_index):
    try:
        film_index = int(film_index)
        film = film_manager.films[film_index]
    except Exception as e:
        return redirect("/static/html/404.html")

    logger.info(f"PAGE REQUEST /film/{film_index} - film {film.name}") 

    return render_template(
            'film.html',
            film=film,
            town="Tel Aviv",
            name_translations=FILM_NAME_TRANSLATIONS,
            get_day_name=get_day_name)
