import datetime
import json
import pytz
from flask import render_template, request
from loguru import logger

from server.show_events import bp
from server.events import event_manager
import server.utils as utils

import filmby

# TODO: This is a hack and should be made good
EVENT_TYPES_TO_VENUE_TYPE_NAMES = {
    filmby.events.Film: "קולנוע",
    filmby.events.Concert: "הופעות"
}

def filter_events(date, hour_filter, types):
    events = []
    indices = []
    event_dates = []
    for i, event in enumerate(event_manager.events):
        if types != None:
            valid = False
            for t in types:
                if t.lower() == type(event).__name__.lower():
                    valid = True
                    break

            if not valid:
                continue

        if date != None:
            dates = event.get_filtered_dates(date) 
            if dates == dict():
                continue
            event_dates.append(dates)
        else:
            event_dates.append(dict())
        events.append(event)
        indices.append(i)

    return indices, events, event_dates

def filter_dates(dates, chosen_date):
    filtered = []
    for date in dates:
        if date.day == chosen_date.day and date.month == chosen_date.month and date.year == chosen_date.year:
            filtered.append(date)
    
    return filtered

def sort_events_by_type(events):
    result = dict()
    for event in events:
        venue_type_name = EVENT_TYPES_TO_VENUE_TYPE_NAMES[type(event)]
        if not venue_type_name in result:
            result[venue_type_name] = [event]
        else:
            result[venue_type_name].append(event)

    return result

@bp.route('/events')
def show_events():
    date = None
    hour_filter = False
    if "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        now = datetime.datetime.now(pytz.timezone("Asia/Jerusalem"))
        if date.day == now.day and date.month == now.month and date.year == now.year:
            date = date.replace(hour=now.hour)
            date = date.replace(minute=now.minute)
            hour_filter = True

    types = None
    if "types" in request.args:
        types = request.args["types"].split(",")

    indices, filtered_events, event_dates = filter_events(date, hour_filter, types)
    logger.debug(f"Found {len(filtered_events)} relevant events")

    logger.info(f"PAGE REQUEST /events - date {date}")

    if "json" in request.args:
        if bool(request.args["json"]):
            result = [event.json_serializable() for event in filtered_events]
            for i, event in enumerate(result):
                event["index"] = indices[i]
            return json.dumps(result)

    filtered_events = sort_events_by_type(filtered_events)

    return render_template(
            'events.html',
            events=filtered_events,
            indices=indices,
            name_translations=utils.get_venue_name_translations(),
            get_day_name=utils.get_day_name,
            type=type,
            filmby=filmby,
            selected_date=date)
