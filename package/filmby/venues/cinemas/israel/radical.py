import time
import requests
import json
import datetime
import threading
from bs4 import BeautifulSoup
from loguru import logger

from filmby.events.film import Film, FilmDetails
from filmby.venues.cinema import Cinema

class RadicalCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "בית רדיקל"}
    NAME = "Radical"
    TOWNS = ["Tel Aviv"]
    UPDATE_INTERVAL = 60 * 60 * 12
    BASE_URL = "https://radical.org.il/"
    CALENDAR_URL = "calendar/"
    INFO_BASE_URL = "https://live.nimi.co.il/event/getEventByHandler/663cc7bf5d7de52d0a22a907/"
    REQUEST_HEADERS = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7",
        "cache-control": "no-cache",
        "cookie": "loc=לב תל אביב".encode("utf-8"),
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.lev.co.il/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
	}
    FILM_WORDS = ["הקרנה", "נקרין", "יוקרן", "תוקרן"]
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self):
        super().__init__()

        self.films_lock = threading.Lock()
        self.films = self.get_films()

    def _check_event(self, info_link, name, link, image_link, films):
        response = requests.get(info_link, headers=self.REQUEST_HEADERS)
        response.encoding = "utf-8"
        data = json.loads(response.text) 
        description = data["description"]
        description = description.replace("\\", "")

        is_film = bool(sum([int(word in description) for word in self.FILM_WORDS]))
        if not is_film:
            return

        self.films_lock.acquire()

        films.append(Film(name))
        films[-1].set_image_url(image_link)
        films[-1].add_link(self.NAME, link)

        date_str = data["start_date"]
        if "." in date_str:
            date_str = date_str[:date_str.index(".")]
        date = datetime.datetime.strptime(date_str, self.DATE_FORMAT)
        films[-1].add_dates(self.NAME, "Tel Aviv", [date])

        films[-1].details.description = description

        self.films_lock.release()

    def get_films(self):
        response = requests.get(self.BASE_URL + self.CALENDAR_URL, headers=self.REQUEST_HEADERS)
        response.encoding = "utf-8"

        html = BeautifulSoup(response.text, "html.parser")
        first_event = html.find_all("div", {"class": "ue_post_grid_item"})[0]
        container = first_event.parent
        events = container.find_all("div", {"class": "ue_post_grid_item"})
        event_info_links = []
        event_links = []
        event_names = []
        event_images = []
        films = []

        for event in events:
            link = event.a["href"]
            event_links.append(link)
            assert link.startswith("https://radical.org.il/events/")
            link = link[len("https://radical.org.il/events/"):]
            if link[-1] == "/":
                link = link[:-1]
            event_info_links.append(self.INFO_BASE_URL + link)
            event_names.append(event.find("div", {"class": "ue_p_title"}).text)

            image_link = event.find("img")["src"]
            # @TODO This is a pretty dumb heuristic
            if image_link[-12] == "-" and image_link[-8] == "x":
                image_link = image_link[:-12] + image_link[-4:]

            event_images.append(image_link)

        threads = []
        for i, link in enumerate(event_info_links):
            thread = threading.Thread(target=self._check_event, args=(link, event_names[i], event_links[i], event_images[i], films))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        self.last_update = time.time()

        return films

    def get_films_by_date(self, date, town):
        if time.time() - self.last_update > self.UPDATE_INTERVAL:
            self.films = self.get_films()

        films = []
        for film in self.films:
            film_dates = film.dates[self.TOWNS[0]][self.NAME]
            for film_date in film_dates:
                if film_date.year == date.year and film_date.month == date.month and film_date.day == date.day:
                    films.append(film)

        return films

    def get_film_details(self, film):
        return None

    def get_provided_film_details(self):
        return []
