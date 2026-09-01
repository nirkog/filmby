import time
import requests
import datetime
import emoji
from bs4 import BeautifulSoup
from loguru import logger

from ...cinema import Cinema
from ...film import Film

class LimboCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע לימבו"}
    NAME = "Limbo"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://hameretz2.org/"
    EVENTS_URL = "wp-json/hm2/v1/events"
    UPDATE_INTERVAL = 60 * 60 * 12
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://hameretz2.org/",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
    }

    def __init__(self):
        super().__init__()

        self.films = self.get_films()

    def get_films(self):
        response = requests.get(self.BASE_URL + self.EVENTS_URL, headers=self.REQUEST_HEADERS)
        response.encoding = "utf-8"

        films = []
        for event in response.json():
            if event["dept"] != "cinema":
                continue

            films.append(Film(event["name"]))

            films[-1].set_image_url(event["images"][0])
            date = datetime.datetime.strptime(event["start"], "%Y-%m-%dT%H:%M")
            films[-1].add_dates(self.NAME, "Tel Aviv", [date])
            films[-1].add_link(self.NAME, event["ticket_sale_link"])

            films[-1].details.description = event["promo"]

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
