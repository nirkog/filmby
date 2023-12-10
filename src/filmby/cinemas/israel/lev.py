import requests
import datetime
import urllib.parse
import json
import parse
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film, FilmDetails

class LevCinema(Cinema):
    NAME = "Lev"
    TOWNS = ["Tel Aviv", "Raanana"]
    THEATER_NAMES = {
            "Tel Aviv": "לב תל אביב",
            "Raanana": "לב רעננה"
    }
    BASE_URL = "https://www.lev.co.il/"
    FILMS_URL = "wp-content/themes/lev/ajax_data.php?clang=he&action=movie_on_location_new&loc={0}&date={1}-{2}-{3}"
    INFO_FORMAT = "{0},{1}|{2}|{3}" # TODO: Add other formats

    def __init__(self):
        super().__init__()
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

    def get_films_by_date(self, date, town):
        encoded_theater_name = urllib.parse.quote(self.THEATER_NAMES[town])
        response = requests.get(self.BASE_URL + self.FILMS_URL.format(encoded_theater_name, date.year, date.month, date.day))
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("li")
        movie_links = html.find_all("a", {"class": "smovielink"})
        films = []

        for i, movie in enumerate(movies):
            if i + 1 > len(movie_links):
                break

            name = urllib.parse.unquote(movie_links[i]["href"][29:-1])
            clean_name = name.replace("-", " ")
            # clean_name = clean_name.replace("-מדובב", "") # ???
            films.append(Film(clean_name))

            films[-1].set_image_url(self.image_urls[name])

            film_date = datetime.datetime.strptime(movie.a.span.text, "%H:%M")
            film_date = datetime.datetime(date.year, date.month, date.day, film_date.hour, film_date.minute)
            films[-1].add_dates(self.NAME, town, [film_date])

            films[-1].add_link(self.NAME, movie_links[i]["href"])

        self._merge_films(films)

        return films

    def get_film_details(self, film):
        if not self.NAME in film.links:
            return None
        
        link = film.links[self.NAME]
        response = requests.get(link)
        html = BeautifulSoup(response.text, "html.parser")

        details = FilmDetails()

        movie_content = html.find("div", {"class": "movie_content"})
        description = movie_content.find("p")
        if description:
            details.description = description.text

        movie_information = html.find("div", {"class": "movie_in"})

        try:
            info_line = movie_information.find("div", {"class": "allwithlinemobile"})
            info = info_line.text.replace("&nbsp", "").strip()

            country, year, language, length = parse.parse(self.INFO_FORMAT, info)
            country = country.strip()
            year = year.strip()
            language = language.strip()
            length = length.strip()
            length = "".join(c for c in length if c in "0123456789")

            details.countries = [country]
            details.year = int(year)
            details.language = language
            details.length = length
        except Exception:
            # print(f"Basic Info Failed {film.name}")
            pass

        try:
            cast_element = movie_information.find("div", {"class": "movie_casts"})
            director = None
            cast = None
            for line in cast_element.text.split("\n"):
                if line.startswith("בימוי: "):
                    director = line[7:]
                if line.startswith("משחק: "):
                    cast = line[6:]

            if director != None:
                details.director = director
            if cast != None:
                details.cast = cast
        except Exception as e:
            # print(f"Cast Failed {film.name}, {e}")
            pass
        
        return details

    def get_provided_film_details(self):
        return ["countries", "year", "language", "length", "director", "cast", "description"]
