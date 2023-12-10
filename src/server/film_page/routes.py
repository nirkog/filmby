import datetime
from flask import render_template, request, redirect

from server.film_page import bp
from server.films import film_manager

@bp.route('/film/<film_index>')
def film_page(film_index):
    try:
        film_index = int(film_index)
        film = film_manager.films[film_index]
    except Exception as e:
        return redirect("/static/html/404.html")

    print(film.dates["Tel Aviv"])

    return render_template('film.html', film=film, town="Tel Aviv")
