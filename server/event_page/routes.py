import datetime
from flask import render_template, request, redirect
from loguru import logger

from server.event_page import bp
from server.events import event_manager
import server.utils as utils

@bp.route('/event/<event_index>')
def event_page(event_index):
    try:
        event_index = int(event_index)
        event = event_manager.events[event_index]
    except Exception as e:
        return redirect("/static/html/404.html")

    logger.info(f"PAGE REQUEST /event/{event_index} - event {event.name}") 

    return render_template(
            'event.html',
            event=event,
            name_translations=utils.get_venue_name_translations(),
            get_day_name=utils.get_day_name)
