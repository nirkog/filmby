import requests
import datetime
import urllib.parse
import json
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class RavHenCinema(Cinema):
    NAME = "Rav Hen"
    TOWNS = ["Tel Aviv", "Givatayim", "Kiryat Ono"]
    THEATER_IDS = {
                "Tel Aviv": 1071,
                "Givatayim": 1058,
                "Kiryat Ono": 1062
            }
    FILMS_URL = "https://www.rav-hen.co.il/rh/data-api-service/v1/quickbook/10104/film-events/in-cinema/{0}/at-date/{1}?attr=&lang=he_IL"
    FILM_DATE_FORMAT = "%Y-%m-%d"
    EVENT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self):
        super().__init__()

    def get_films_by_date(self, date, town):
        url = self.FILMS_URL.format(self.THEATER_IDS[town], date.strftime(self.FILM_DATE_FORMAT))
        response = requests.get(url).json()

        films = dict()
        events = response["body"]["events"]
        
        for film in response["body"]["films"]:
            films[film["id"]] = film

        result = []
        for event in events:
            film = films[event["filmId"]]
            result.append(Film(film["name"]))

            result[-1].set_image_url(film["posterLink"])

            date = datetime.datetime.strptime(event["eventDateTime"], self.EVENT_DATE_FORMAT)
            result[-1].add_dates(self.NAME, town, [date])

            result[-1].add_link(self.NAME, film["link"])

        self._merge_films(result)

        return result
