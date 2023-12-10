import datetime
from flask import render_template, request

from server.show_films import bp
from server.films import film_manager

def filter_films(date, town):
    films = []
    indices = []
    for i, film in enumerate(film_manager.films):
        if town in film.dates and film.has_screenings_on_date(date):
            films.append(film)
            indices.append(i)

    return indices, films

@bp.route('/films')
def show_films():
    date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
    indices, filtered_films = filter_films(date, request.args["town"])
    print(f"Found {len(filtered_films)} relevant films")
    return render_template('films.html', films=filtered_films, indices=indices)
