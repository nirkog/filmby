import requests
import datetime
import urllib.parse
import parse
from bs4 import BeautifulSoup

from filmby.events.film import Film, FilmDetails
from filmby.venues.cinema import Cinema

class LevCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע לב"}
    NAME = "Lev"
    TOWNS = ["Tel Aviv", "Raanana"]
    THEATER_NAMES = {
            "Tel Aviv": "לב תל אביב",
            "Raanana": "לב רעננה"
    }
    BASE_URL = "https://www.lev.co.il/"
    FILMS_URL = "wp-content/themes/lev/ajax_data.php?clang=he&action=movie_on_location_new&loc={0}&date={1}-{2}-{3}"
    INFO_FORMAT = "{0},{1}|{2}|{3}" # TODO: Add other formats
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

    def __init__(self):
        super().__init__()
        self.image_urls = self.get_image_urls()

    def get_image_urls(self):
        response = requests.get(self.BASE_URL + "/movie/", headers=self.REQUEST_HEADERS)
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("li", {"class": "featureItem"})
        urls = dict()

        for movie in movies:
            name = urllib.parse.unquote(movie.div.a["href"][29:-1])
            url = movie.div.a.img["data-src"]
            urls[name] = url

        return urls

    def get_events_by_date(self, date):
        encoded_theater_name = urllib.parse.quote(self.THEATER_NAMES["Tel Aviv"])
        response = requests.get(self.BASE_URL + self.FILMS_URL.format(encoded_theater_name, date.year, date.month, date.day), headers=self.REQUEST_HEADERS)
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("li")
        movie_links = html.find_all("a", {"class": "smovielink"})
        films = []

        for i, movie in enumerate(movies):
            if i + 1 > len(movie_links):
                break

            name = urllib.parse.unquote(movie_links[i]["href"][29:-1])
            clean_name = name.replace("-", " ")
            films.append(Film(clean_name))

            films[-1].set_image_url(self.image_urls[name])

            film_date = datetime.datetime.strptime(movie.a.span.text, "%H:%M")
            film_date = datetime.datetime(date.year, date.month, date.day, film_date.hour, film_date.minute)
            films[-1].add_dates(self.NAME, [film_date])

            films[-1].add_link(self.NAME, movie_links[i]["href"])

        self._merge_films(films)

        return films

    def get_event_details(self, film):
        cache = self._get_details_from_cache(film)
        if cache != None:
            return cache

        if not self.NAME in film.links:
            return None
        
        link = film.links[self.NAME]
        response = requests.get(link, headers=self.REQUEST_HEADERS)
        html = BeautifulSoup(response.text, "html.parser")

        details = FilmDetails()

        movie_content = html.find("div", {"class": "movie_content"})
        ps = movie_content.find_all("p")
        description = ""
        for p in ps:
            span = p.find("span")
            if None == span:
                description += p.text + "\n"
            else:
                description += span.text + "\n"
        details.description = description

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
            details.length = int(length)
        except Exception:
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
            pass

        self._add_to_details_cache(film, details)
        
        return details

    def get_provided_event_details(self):
        return ["countries", "year", "language", "length", "director", "cast", "description"]
