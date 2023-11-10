import requests
import datetime
import urllib.parse
import json
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class JaffaCinema(Cinema):
    NAME = "Jaffa"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://www.jaffacinema.com/"
    DATE_FORMAT = "%d/%m/%y"
    HOUR_FORMAT = "%H:%M"

    def __init__(self):
        super().__init__()

    def get_image_urls(self, html):
        urls = dict()
        screenings = html.find("div", {"id": "screenings"})
        for screening in screenings.children:
            image = screening.div.div.img["src"]
            name = screening.div.div.div.h2.text
            urls[name] = image

        return urls

    def get_films_by_date(self, date, town):
        response = requests.get(self.BASE_URL)
        html = BeautifulSoup(response.text, "html.parser")
        image_urls = self.get_image_urls(html)
        screening_elements = html.find_all("select", {"class": "screenings"})
        screenings = dict()

        for element in screening_elements:
            clean_date = "".join([c for c in element["id"] if c in "0123456789/"])
            clean_date = datetime.datetime.strptime(clean_date, self.DATE_FORMAT)
            screenings[clean_date] = element

        chosen = None
        for d in screenings:
            if d.year == date.year and d.month == date.month and d.day == date.day:
                chosen = screenings[d]
                break
        
        if chosen == None:
            return None

        films = []
        screening_elements = chosen.find_all("option")
        for element in screening_elements:
            link = element["value"]
            name, hour = element.text.split(" | ")

            films.append(Film(name))

            films[-1].set_image_url(image_urls[name])

            hour = datetime.datetime.strptime(hour, self.HOUR_FORMAT)
            film_date = datetime.datetime(date.year, date.month, date.day, hour.hour, hour.minute)
            films[-1].add_dates(self.NAME, town, [film_date])

            films[-1].add_link(self.NAME, link)

        self._merege_films(films)

        return films
