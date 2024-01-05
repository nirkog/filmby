import requests
import datetime
import urllib.parse
import json
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film, FilmDetails

LANGUAGE_TRANSLATIONS = {
    "original-lang-uk": "UA",
    "original-lang-ar": "ערבית",
    "original-lang-bg": "בולגרית",
    "original-lang-zh": "סינית",
    "original-lang-bs": "BA",
    "original-lang-cs": "צ'כית",
    "original-lang-da": "דנית",
    "original-lang-nl": "הולנדית",
    "original-lang-en-fa": " עברית/פרסית",
    "original-lang-sq": "SK",
    "original-lang-en-fr": "אנגלית/צרפתית",
    "original-lang-en-de-fr": "אנגלית/גרמנית/צרפתית",
    "original-lang-en-ru": "אנגלית/רוסית",
    "original-lang-en-uk": " אנגלית",
    "original-lang-en-au": "אנגלית",
    "original-lang-en-ca": "אנגלית",
    "original-lang-en-gb": "אנגלית",
    "original-lang-en-us": "אנגלית",
    "original-lang-fr-ca": "צרפתית",
    "original-lang-fr-fr": "צרפתית",
    "original-lang-de": "גרמנית",
    "original-lang-he": "עברית",
    "original-lang-he-en": "עברית/אנגלית",
    "original-lang-he-fr": "עברית/צרפתית",
    "original-lang-he-ru": "עברית/רוסית",
    "original-lang-hi": "הודית",
    "original-lang-hu": "הונגרית",
    "original-lang-is": "איסלנדית",
    "original-lang-it": "איטלקית",
    "original-lang-ja": "יפנית",
    "original-lang-ko": "קוריאנית",
    "original-lang-ml": "מלאיאלאם",
    "original-lang-mix": "מעורב",
    "original-lang-nn": "נורווגית",
    "original-lang-pk": "פקיסטנית",
    "original-lang-fa": "פרסית",
    "original-lang-pl": "פולנית",
    "original-lang-pt": "פורטוגזית",
    "original-lang-pa": "פונג'אבי",
    "original-lang-ro": "רומנית",
    "original-lang-ru": "רוסית",
    "original-lang-ru-fr": "רוסית/צרפתית",
    "original-lang-sk": "סלובקית",
    "original-lang-es": "ספרדית",
    "original-lang-es-cl": "ספרדית",
    "original-lang-es-pe": "ספרדית",
    "original-lang-sv": "שבדית",
    "original-lang-ta": "טמילית",
    "original-lang-te": "טלוגו",
    "original-lang-tr": "תורכית",
    "original-lang-without": "ללא",
    "original-lang-th": " תאילנדית",
    "original-lang-sl": " סלובנית",
    "original-lang-ka": " גיאורגית",
    "original-lang-fi": " פינית",
    "original-lang-mn": " מונגולית",
    "original-lang-sr": " סרבית",
    "original-lang-hr": " קרואטית",
    "original-lang-id": " אינדונזית",
    "original-lang-dz": " דזונגקה",
    "original-lang-es-mx": "ספרדית"
}

class RavHenCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "רב חן"}
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

    def get_film_details(self, film):
        response = requests.get(film.links[self.NAME])
        html = BeautifulSoup(response.text, "html.parser")
        body = html.find("body")
        scripts = [x for x in body.find_all("script") if "var featureName" in x.text]

        if len(scripts) == 0:
            return
        
        script = scripts[0]
        lines = script.text.split("\n")

        details = FilmDetails
        for line in lines:
            if "filmDetails" in line:
                obj = line[line.index("{"):-1]
                film_details = json.loads(obj)
                details.countries = [film_details["releaseCountry"]]
                details.year = film_details["releaseYear"]
                details.language = LANGUAGE_TRANSLATIONS[film_details["originalLanguage"][0]]
                details.length = film_details["length"]
                details.director = film_details["directors"]
                details.cast = film_details["cast"]
                details.description = film_details["synopsis"]
                details.description = details.description.replace("<p>", "")
                details.description = details.description.replace("<br>", "")
                break

        return details

    def get_provided_film_details(self):
        return ["countries", "year", "language", "length", "director", "cast", "description"]
