from flask import render_template
import datetime
from loguru import logger

import filmby

from server.index import bp
import server.films as films

@bp.route('/')
def index():
    logger.info("PAGE REQUEST /index")
    min_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    max_date = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(films.SPAN_IN_DAYS), "%Y-%m-%d")
    return render_template('index.html', min_date=min_date, max_date=max_date, cinemas=filmby.CINEMAS["Israel"])
