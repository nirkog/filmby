import time
import requests
import datetime
import urllib.parse
import json
import re
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class CanadaCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע קנדה"}
    NAME = "Canada"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://www.kolnoakanada.com/"
    DATE_FORMAT = "%d.%m"
    HOUR_PATTERN = "\d\d:\d\d"
    UPDATE_INTERVAL = 60 * 60

    def __init__(self):
        super().__init__()
        self.films = self.get_films()
        self.last_update = time.time()

    def get_films(self):
        response = requests.get(self.BASE_URL)
        response.encoding = "utf-8"

        html = BeautifulSoup(response.text, "html.parser")
        events_app_elements = html.find_all("div", {"class": "events-app"})

        films = []
        for events_app_element in events_app_elements:
            movie_content = events_app_element.find("div", {"class": "movie-content"})
            poster_container = events_app_element.find("div", {"class": "poster-container"})
            title_bar = events_app_element.find("div", {"class": "title-bar"})
            buttons_container = events_app_element.find("div", {"class": "buttons-container"})

            name_element = movie_content.strong.p
            name = name_element.text
            name = name[:name.find("(")].strip()

            films.append(Film(name))

            films[-1].set_image_url(poster_container.img["src"])
            
            title = title_bar.div.b
            date = "".join([c for c in title.text if c in "0123456789."])
            date = datetime.datetime.strptime(date, self.DATE_FORMAT)

            hour = movie_content.div.text
            hour = re.findall(self.HOUR_PATTERN, hour)
            
            if len(hour) > 0:
                hour = hour[0]
                hour, minute = hour.split(":")
                date = datetime.datetime(datetime.datetime.today().year, date.month, date.day, int(hour), int(minute))
            else:
                date = datetime.datetime(datetime.datetime.today().year, date.month, date.day, 0, 0)
            films[-1].add_dates(self.NAME, self.TOWNS[0], [date])

            link = buttons_container.find("a")["href"]
            films[-1].add_link(self.NAME, link)

            description = movie_content.find("p", {"id": "extra-details"}).text
            films[-1].details.description = description

            try:
                year = name_element.text[name_element.text.find("(")+1:name_element.text.find(")")]
                films[-1].details.year = int(year)
            except Exception:
                pass

        self._merge_films(films)

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
