import time
import threading
import pickle
import os
import time
from pathlib import Path
from datetime import date, timedelta

from loguru import logger

import filmby

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
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)

class FilmManager:
    def __init__(self, cache_path="cache/films.bin"):
        self.manual_films = []
        self.films = []
        self.cache_path = cache_path
        self.started = False

        if os.path.exists("/tmp/filmby_update_running"):
            os.remove("/tmp/filmby_update_running")

    def start_film_updating_at_interval(self, interval, ignore_cache=False):
        if self.started:
            return
        self.started = True

        cache = None
        first_sleep_duration = 0
        if os.path.exists(self.cache_path) and not ignore_cache:
            with open(self.cache_path, "rb") as f:
                cache = pickle.load(f)
                self.films = cache["films"]
                logger.info(f"Loading cache with {len(self.films)} films")

                if time.time() - cache["timestamp"] < interval:
                    first_sleep_duration = interval - (time.time() - cache["timestamp"])
                    logger.info(f"Loading films from cache, next update will be in {int(first_sleep_duration)} seconds")

        if os.path.exists("./data/manual_films.bin"):
            with open("./data/manual_films.bin", "rb") as f:
                manual_films = pickle.load(f)
            self.manual_films = manual_films
            self.films.extend(manual_films)

        logger.info(f"Initialized films with {len(self.manual_films)} manual films")

        thread = IntervalThread(interval, first_sleep_duration, self.update_films)
        thread.start()

    def update_films(self):
        if os.path.exists("/tmp/filmby_update_running"):
            logger.debug("Redundant thread is exiting")
            exit()
        with open("/tmp/filmby_update_running", "w") as f:
            f.write("RUNNING")
        start = time.time()

        logger.info("Starting film update procedure")

        country = "Israel"
        town = "Tel Aviv"
        cinemas = dict()

        for cinema in filmby.CINEMAS[country]:
            if town in cinema.TOWNS:
                try:
                    cinemas[cinema.NAME] = cinema()
                except Exception as e:
                    logger.error(f"Could not initialize {cinema.NAME} cinema, error: {str(e)}")

        threads = []
        new_films = []
        condition = threading.Condition()
        for cinema in cinemas:
            for i in range(SPAN_IN_DAYS):
                if threading.active_count() > MAX_THREAD_COUNT:
                    with condition:
                        condition.wait()
                threads.append(threading.Thread(target=self._get_films_by_date, args=(cinemas[cinema], date.today() + timedelta(i), town, new_films, condition,)))
                threads[-1].start()

        for thread in threads:
            thread.join()

        threads = []
        for film in new_films:
            for cinema in film.links:
                if len([x for x in cinemas[cinema].get_provided_film_details() if x in film.details.get_missing_details()]) == 0:
                    continue

                if threading.active_count() > MAX_THREAD_COUNT:
                    with condition:
                        condition.wait()
                threads.append(threading.Thread(target=self._get_film_details, args=(cinemas[cinema], film, condition,)))
                threads[-1].start()

        for thread in threads:
            thread.join()

        new_films = self._merge_films(new_films)
        self.films = new_films
        self.films.extend(self.manual_films)

        cache_path = Path(self.cache_path)
        if not os.path.exists(cache_path.parent):
            os.makedirs(cache_path.parent, exist_ok=True)

        cache_films = [film for film in self.films if not film in self.manual_films]
        cache = {"films": cache_films, "timestamp": time.time()}
        with open(self.cache_path, "wb") as f:
            pickle.dump(cache, f)

        logger.info(f"Finished updating with {len(self.films)} films, took {time.time() - start:.1f}s")

        if os.path.exists("/tmp/filmby_update_running"):
            os.remove("/tmp/filmby_update_running")

    def _merge_films(self, films):
        new_films = []
        for film in films:
            found = False
            for new_film in new_films:
                if new_film.is_identical(film):
                    found = True
                    new_film.merge(film)
            if not found:
                new_films.append(film)
        return new_films

    def _get_films_by_date(self, cinema, date, town, arr, condition):
        result = cinema.get_films_by_date(date, town)
        if result != None:
            arr.extend(result)
        with condition:
            condition.notify_all()

    def _get_film_details(self, cinema, film, condition):
        new_details = cinema.get_film_details(film)
        if new_details != None:
            film.details.merge(new_details)

        with condition:
            condition.notify_all()

film_manager = FilmManager()
