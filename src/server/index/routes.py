from flask import render_template
import datetime

from server.index import bp
import server.films as films

@bp.route('/')
def index():
    min_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    max_date = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(7), "%Y-%m-%d")
    return render_template('index.html', min_date=min_date, max_date=max_date)
