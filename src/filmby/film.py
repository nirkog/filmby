import requests
import os
import logging

from loguru import logger
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

CONTENT_TYPES_TO_FILE_ENGINGS = {
    "image/jpeg": ".jpg"
}

FILM_LENGTH_VARIANCE = 4

LANGUAGE_FILM_NAME_WORDS = ["עברית", "אנגלית", "עם", "-", ":", "מדובב", "כתוביות"]

def same_date(first, second):
    return (first.year == second.year) and (first.month == second.month) and (first.day == second.day)

class FilmDetails:
    def __init__(self, description=None, director=None, cast=None, length=None, countries=None, language=None, year=None):
        self.description = description 
        self.director = director 
        self.cast = cast 
        self.length = length 
        self.countries = countries 
        self.language = language 
        self.year = year

    def get_missing_details(self):
        details = vars(self)
        result = []
        for var in details:
            if details[var] == None:
                result.append(var)

        return result

    def merge(self, other):
        details = vars(self)
        other_details = vars(other)
        for var in details:
            if other_details[var] == None:
                continue

            if var == "description":
                if details[var] == None:
                    setattr(self, var, other_details[var])
                elif len(other_details[var]) > len(details[var]):
                    setattr(self, var, other_details[var])
            else:
                if details[var] == None:
                    setattr(self, var, other_details[var])

    def get_countries_string(self):
        to_replace = ["[", "]", "'"]
        result = str(self.countries)
        for c in to_replace:
            result = result.replace(c, "")
        return result

class Film:
    def __init__(self, name):
        self.name = name
        self.image_url = None
        self.dates = dict()
        self.links = dict()
        self.details = FilmDetails()

    def add_link(self, cinema_name, link):
        self.links[cinema_name] = link

    def download_image(self, path, file_ending=None):
        if not self.image_url:
            return
        
        # TODO: Add verification everywhere
        response = requests.get(self.image_url)

        if file_ending == None:
            # TODO: This is dumb
            file_ending = CONTENT_TYPES_TO_FILE_ENGINGS[response.headers["Content-Type"]]

        with open("path", os.path.join(path, self.name + file_ending)) as f:
            f.write(response.content)

    def set_image_url(self, url):
        self.image_url = url

    def add_dates(self, cinema_name, town, dates):
        if not town in self.dates:
            self.dates[town] = dict()

        if not cinema_name in self.dates[town]:
            self.dates[town][cinema_name] = dates
        else:
            self.dates[town][cinema_name].extend(dates)

        self.dates[town][cinema_name] = list(set(self.dates[town][cinema_name]))

    def merge(self, other):
        # TODO: Merge based on image url
        self.details.merge(other.details)

        for town in other.dates:
            for cinema in other.dates[town]:
                self.add_dates(cinema, town, other.dates[town][cinema])

        for cinema in other.links:
            if not cinema in self.links:
                self.links[cinema] = other.links[cinema]

        # TODO: Is this good?
        if len(other.name) < len(self.name):
            self.name = other.name

    def _without_language_name_heuristic(self, name1, name2):
        for word in LANGUAGE_FILM_NAME_WORDS:
            name1 = name1.replace(word, "")
            name2 = name2.replace(word, "")

        return fuzz.partial_ratio(name1, name2) > 90

    def is_identical(self, other):
        result = False

        # TODO: Maybe needs improvement

        if not result and self.name == other.name:
            result = True
        
        if not result and self.name.replace("-", "") == other.name.replace("-", ""):
            result = True
        
        if not result and self.name.replace("-", " ") == other.name.replace("-", " "):
            result = True
        
        if not result and fuzz.partial_ratio(self.name, other.name) > 85:
            # print("MERGING", self.name, other.name)
            result = True

        if not result and self._without_language_name_heuristic(self.name, other.name):
            # logger.debug(f"Merging with new heuristic {self.name}, {other.name}")
            result = True

        if result and self.details.length and other.details.length:
            if abs(self.details.length - other.details.length) > FILM_LENGTH_VARIANCE:
                # print(f"Not identical, legnths too far apart #1 {self.name}, #2 {other.name}")
                result = False
        if result and self.details.year and other.details.year:
            if self.details.year != other.details.year:
                # print(f"Not identical, years differ #1 {self.name}, #2 {other.name}, {self.details.year}, {other.details.year}")
                result = False

        return result
    
    def has_screenings_on_date(self, date):
        for town in self.dates:
            for cinema in self.dates[town]:
                for d in self.dates[town][cinema]:
                    if same_date(d, date):
                        return True

        return False
