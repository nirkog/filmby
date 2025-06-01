import requests
import datetime
import urllib.parse
import json
import parse
import time
from bs4 import BeautifulSoup
from loguru import logger

from ...cinema import Cinema
from ...film import Film, FilmDetails

class TLVMuseumCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "מוזיאון תל אביב"}
    NAME = "TLVMuseum"
    TOWNS = ["Tel Aviv"]
    UPDATE_INTERVAL = 60 * 60
    BASE_URL = "https://www.tamuseum.org.il"
    FILMS_URL = "/api/v2/he/events/filter/?category=film&offset=0"
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
    PARTIAL_DATE_FORMAT = "%Y-%m-%d"
    FULL_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self):
        super().__init__()

        self.films = self.get_films()

    def get_films(self):
        response = requests.get(self.BASE_URL + self.FILMS_URL, headers=self.REQUEST_HEADERS)
        response = response.json()
        films = []
        film_id_to_index = dict()

        for date in response["items"]:
            for film_json in response["items"][date]:
                if film_json["id"] in film_id_to_index:
                    index = film_id_to_index[film_json["id"]]
                else:
                    name = film_json["title"]
                    if "<i>" in name:
                        name = name[name.index("<i>") + 3:name.index("</i>")]
                    films.append(Film(name))
                    film_id_to_index[film_json["id"]] = len(films) - 1
                    index = -1

                film_date = datetime.datetime.strptime(film_json["date"], self.FULL_DATE_FORMAT)
                films[index].add_dates(self.NAME, "Tel Aviv", [film_date])

                films[index].add_link(self.NAME, self.BASE_URL + film_json["url"])


        self.last_update = time.time()

        return films

    def get_films_by_date(self, date, town):
        if time.time() - self.last_update > self.UPDATE_INTERVAL:
            self.films = self.get_films()

        films = []
        for film in self.films:
            if film.has_screenings_on_date(date):
                films.append(film)

        return films

    def get_film_details(self, film):
        cache = self._get_details_from_cache(film)
        if cache != None:
            return cache

        if not self.NAME in film.links:
            return None
        
        link = film.links[self.NAME]
        response = requests.get(link, headers=self.REQUEST_HEADERS)
        html = BeautifulSoup(response.text, "html.parser")

        details = FilmDetails()

        picture = html.find("picture", {"class": "main_image"})
        image_url = picture.find("img")["src"]

        film.set_image_url(image_url)

        description_div = html.find("div", {"class": "copy_text"}).find("div", {"class": "rich-text"})
        description_ps = description_div.find_all("p")
        description = ""
        in_description = False
        year = None
        director = None
        language = None
        length = None
        countries = None

        for p in description_ps:
            if "טריילר" in p.text:
                in_description = True
                continue

            if in_description and p.text == "—":
                break

            if in_description:
                description += p.text + "<br/>"

            if "בימוי" in p.text:
                try:
                    area = p.text[p.text.index("|") - 8:p.text.index("|")]
                    area = "".join([x for x in area if x.isnumeric()])
                    year = int(area)
                except Exception:
                    logger.warning(f"Could not parse year for {film.name}")

                try:
                    more_details = p.text[p.text.index("בימוי") + 7:].split(", ")
                    director = more_details[0]
                    countries = [more_details[1]]
                    language = more_details[3]
                    length = int("".join([x for x in more_details[2] if x.isnumeric()]))
                except Exception:
                    logger.warning(f"Could not parse more details for {film.name}")

        details.description = description
        details.year = year
        details.director = director
        details.countries = countries
        details.language = language
        details.length = length
        
        return details

    def get_provided_film_details(self):
        return ["countries", "year", "language", "length", "director", "cast", "description"]
