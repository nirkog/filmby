import requests
import os
import copy
import string

from fuzzywuzzy import fuzz

from filmby.event import Event, EventDetails

CONTENT_TYPES_TO_FILE_ENGINGS = {
    "image/jpeg": ".jpg"
}

FILM_LENGTH_VARIANCE = 4
FILM_YEAR_VARIANCE = 4

LANGUAGE_FILM_NAME_WORDS = ["עברית", "אנגלית", "עם", "-", ":", "מדובב", "כתוביות"]

HEBREW_ENGLISH_LETTERS = string.ascii_lowercase + string.ascii_uppercase + "_.:|!?,0123456789" + "אבגדהוזחטיכלמנסעפצקרשת"

def same_date(first, second):
    return (first.year == second.year) and (first.month == second.month) and (first.day == second.day)

def get_hebrew_english_score(text):
    if len(text) == 0:
        return 0

    return (len([x for x in text if x in HEBREW_ENGLISH_LETTERS]) / len(text)) * 100

class FilmDetails(EventDetails):
    def __init__(self, description=None, director=None, cast=None, length=None, countries=None, language=None, year=None):
        super().__init__()

        self.description = description 
        self.director = director 
        self.cast = cast 
        self.length = length 
        self.countries = countries 
        self.language = language 
        self.year = year

    def _get_better_description(self, first, second):
        if get_hebrew_english_score(first) < 50:
            return second

        if get_hebrew_english_score(first) < 50:
            return first

        if len(first) > len(second):
            return first

        if len(second) > len(first):
            return first
        
        return first

    def merge(self, other):
        details = vars(self)
        other_details = vars(other)
        for var in details:
            if other_details[var] == None:
                continue

            if var == "description":
                if details[var] == None:
                    setattr(self, var, other_details[var])
                else:
                    setattr(self, var, self._get_better_description(details[var], other_details[var]))
            else:
                if details[var] == None:
                    setattr(self, var, other_details[var])

    def get_countries_string(self):
        to_replace = ["[", "]", "'"]
        result = str(self.countries)
        for c in to_replace:
            result = result.replace(c, "")
        return result

class Film(Event):
    def __init__(self, name):
        super().__init__(name)

        self.details = FilmDetails()
        self.type_string = "film"

    def __str__(self):
        return f"{self.name}, {self.details.director}, {self.details.length}, {self.details.language}, {self.details.year}, {self.links}, {self.dates}"

    def merge(self, other):
        self.details.merge(other.details)

        for cinema in other.dates:
            self.add_dates(cinema, other.dates[cinema])

        for cinema in other.links:
            if not cinema in self.links:
                self.links[cinema] = other.links[cinema]

        if get_hebrew_english_score(self.name) < 70:
            self.name = other.name
        elif get_hebrew_english_score(other.name) < 70:
            pass
        elif len(other.name) < len(self.name):
            self.name = other.name

    def _without_language_name_heuristic(self, name1, name2):
        for word in LANGUAGE_FILM_NAME_WORDS:
            name1 = name1.replace(word, "")
            name2 = name2.replace(word, "")

        return fuzz.partial_ratio(name1, name2) > 90

    def _same_cinema_heuristic(self, other):
        self_cinemas = []
        for cinema in self.dates:
            self_cinemas.append(cinema)

        other_cinemas = []
        for cinema in other.dates:
            other_cinemas.append(cinema)

        return self_cinemas == other_cinemas

    def is_identical(self, other):
        result = False

        # TODO: Maybe needs improvement

        if not result and self.name == other.name:
            result = True
        
        if not result and self.name.replace("-", "") == other.name.replace("-", ""):
            result = True
        
        if not result and self.name.replace("-", " ") == other.name.replace("-", " "):
            result = True

        fuzzy_score_partial = fuzz.partial_ratio(self.name, other.name)
        fuzzy_score = fuzz.ratio(self.name, other.name)
        if not result and fuzzy_score_partial > 70:
            if self._same_cinema_heuristic(other) and fuzzy_score_partial < 85:
                pass
            elif fuzzy_score_partial < 90 and fuzzy_score < 50:
                pass
            else:
                result = True

        if not result and self._without_language_name_heuristic(self.name, other.name):
            result = True

        if result and self.details.length and other.details.length:
            if abs(self.details.length - other.details.length) > FILM_LENGTH_VARIANCE:
                result = False
        if result and self.details.year and other.details.year:
            if abs(self.details.year - other.details.year) > FILM_YEAR_VARIANCE:
                result = False

        return result
