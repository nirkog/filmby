import datetime
from flask import render_template, request, redirect
from loguru import logger

from server.film_page import bp
from server.films import film_manager
import server.utils as utils

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
            name_translations=utils.get_cinema_name_translations(),
            get_day_name=utils.get_day_name)
