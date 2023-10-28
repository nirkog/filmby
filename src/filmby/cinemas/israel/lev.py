import requests
import datetime
import urllib.parse
import json
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class LevCinema(Cinema):
    NAME = "Lev"
    TOWNS = ["Tel Aviv", "Raanana"]
    THEATER_NAMES = {
            "Tel Aviv": "לב תל אביב",
            "Raanana": "לב רעננה"
    }
    BASE_URL = "https://www.lev.co.il/"
    FILMS_URL = "wp-content/themes/lev/ajax_data.php?clang=he&action=movie_on_location_new&loc={0}&date={1}-{2}-{3}"

    def __init__(self, town):
        super().__init__(town)
        self.image_urls = self.get_image_urls()

    def get_image_urls(self):
        response = requests.get(self.BASE_URL + "/movie/")
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("li", {"class": "featureItem"})
        urls = dict()

        for movie in movies:
            name = urllib.parse.unquote(movie.div.a["href"][29:-1])
            url = movie.div.a.img["data-src"]
            urls[name] = url

        return urls

    def get_films_by_date(self, date):
        encoded_theater_name = urllib.parse.quote(self.THEATER_NAMES[self.town])
        response = requests.get(self.BASE_URL + self.FILMS_URL.format(encoded_theater_name, date.year, date.month, date.day))
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("li")
        movie_links = html.find_all("a", {"class": "smovielink"})
        films = []

        for i, movie in enumerate(movies):
            name = urllib.parse.unquote(movie_links[i]["href"][29:-1])
            films.append(Film(name))

            films[-1].set_image_url(self.image_urls[name])

            film_date = datetime.datetime.strptime(movie.a.span.text, "%H:%M")
            film_date = datetime.datetime(date.year, date.month, date.day, film_date.hour, film_date.minute)
            films[-1].add_dates(self.NAME, [film_date])

            films[-1].add_link(self.NAME, movie_links[i])

        return films
