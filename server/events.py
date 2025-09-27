import time
import threading
import pickle
import os
import time
from pathlib import Path
from datetime import date, timedelta
from loguru import logger

import filmby

from .utils import send_email

MAX_THREAD_COUNT = 100
SPAN_IN_DAYS = 14

class IntervalThread(threading.Thread):
    def __init__(self, interval, first_sleep_duration, func, args=(), kwargs=dict()):
        super(IntervalThread, self).__init__()
        self.interval = interval
        self.first_sleep_duration = first_sleep_duration
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if self.first_sleep_duration > 0:
            time.sleep(self.first_sleep_duration)
        while True:
            # TODO: Maybe take interval from end to start
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as e:
                import traceback
                traceback.print_tb(e.__traceback__)
                logger.error(f"Some fucked up error {e}")
            time.sleep(self.interval)

class EventManager:
    def __init__(self, cache_path="cache/events.bin"):
        self.manual_events = []
        self.events = []
        self.cache_path = cache_path
        self.debug = False

        if os.path.exists("/tmp/filmby_update_running"):
            os.remove("/tmp/filmby_update_running")

    def start_event_updating_at_interval(self, interval, ignore_cache=False):
        cache = None
        first_sleep_duration = 0
        if os.path.exists(self.cache_path) and not ignore_cache:
            with open(self.cache_path, "rb") as f:
                cache = pickle.load(f)
                self.events = cache["events"]
                logger.info(f"Loading cache with {len(self.events)} events")

                if time.time() - cache["timestamp"] < interval:
                    first_sleep_duration = interval - (time.time() - cache["timestamp"])
                    logger.info(f"Loading events from cache, next update will be in {int(first_sleep_duration)} seconds")

        if os.path.exists("./data/manual_events.bin"):
            with open("./data/manual_events.bin", "rb") as f:
                manual_events = pickle.load(f)
            self.manual_events = manual_events
            self.events.extend(manual_events)

        logger.info(f"Initialized events with {len(self.manual_events)} manual events")

        thread = IntervalThread(interval, first_sleep_duration, self.update_events)
        thread.start()

    def update_events(self):
        start = time.time()

        logger.info("Starting event update procedure")

        venues = dict()
        for venue in filmby.VENUES:
            try:
                venues[venue.NAME] = venue()
            except Exception as e:
                logger.error(f"Could not initialize {venue.NAME} venue, error: {str(e)}")

        threads = []
        new_events = []
        condition = threading.Condition()
        for venue_name in venues:
            for i in range(SPAN_IN_DAYS):
                if threading.active_count() > MAX_THREAD_COUNT:
                    with condition:
                        condition.wait()
                threads.append(threading.Thread(target=self._get_events_by_date, args=(venues[venue_name], date.today() + timedelta(i), new_events, condition,)))
                threads[-1].start()

        for thread in threads:
            thread.join()

        threads = []
        for event in new_events:
            for venue in event.links:
                if len([x for x in venues[venue].get_provided_event_details() if x in event.details.get_missing_details()]) == 0:
                    continue

                if threading.active_count() > MAX_THREAD_COUNT:
                    with condition:
                        condition.wait()
                threads.append(threading.Thread(target=self._get_event_details, args=(venues[venue], event, condition,)))
                threads[-1].start()

        for thread in threads:
            thread.join()

        new_events = self._merge_films(new_events)
        self.events = new_events

        excluded_venues = ["Jaffa Hill"]
        unfound_venue_names = [venue for venue in venues if venue not in excluded_venues]
        for event in new_events:
            for venue_name in unfound_venue_names:
                if venue_name in event.dates:
                    if len(event.dates[venue_name]) > 0:
                        unfound_venue_names.remove(venue_name)
        
        if len(unfound_venue_names) > 0:
            broken_venues = ", ".join(unfound_venue_names)
            logger.warning(f"{len(unfound_venue_names)} venues are possibly broken - {broken_venues}")

            if not self.debug:
                try:
                    content = "\n".join(unfound_venue_names)
                    subject = f"{len(unfound_venue_names)} venues are possibly broken"
                    send_email(subject, content)
                except Exception as e:
                    logger.error(f"Failed to send alert email, {e}") 

        self.events.extend(self.manual_events)

        cache_path = Path(self.cache_path)
        if not os.path.exists(cache_path.parent):
            os.makedirs(cache_path.parent, exist_ok=True)

        cache_events = [event for event in self.events if not event in self.manual_events]
        cache = {"events": cache_events, "timestamp": time.time()}
        with open(self.cache_path, "wb") as f:
            pickle.dump(cache, f)

        logger.info(f"Finished updating with {len(self.events)} events, took {time.time() - start:.1f}s")

    def _merge_films(self, events):
        new_events = []
        for event in events:
            if not type(event) == filmby.events.Film:
                new_events.append(event)
                continue

            found = False
            for new_event in new_events:
                if not type(new_event) == filmby.events.Film:
                    continue

                if new_event.is_identical(event):
                    found = True
                    new_event.merge(event)

            if not found:
                new_events.append(event)
        return new_events

    def _get_events_by_date(self, venue, date, arr, condition):
        result = venue.get_events_by_date(date)
        if result != None:
            arr.extend(result)
        with condition:
            condition.notify_all()

    def _get_event_details(self, venue, event, condition):
        new_details = venue.get_event_details(event)
        if new_details != None:
            event.details.merge(new_details)

        with condition:
            condition.notify_all()

    def set_debug(self, new_value):
        self.debug = new_value

event_manager = EventManager()
