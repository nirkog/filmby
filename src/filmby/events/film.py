import requests
import os
import copy
import string

from fuzzywuzzy import fuzz

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

class Film:
    def __init__(self, name):
        self.name = name
        self.image_url = None
        self.dates = dict()
        self.links = dict()
        self.details = FilmDetails()

    def __str__(self):
        return f"{self.name}, {self.details.director}, {self.details.length}, {self.details.language}, {self.details.year}, {self.links}, {self.dates}"

    def json_serializable(self):
        result = copy.deepcopy(self.__dict__)
        result["details"] = copy.deepcopy(self.details.__dict__)

        for town in result["dates"]:
            for cinema in result["dates"][town]:
                result["dates"][town][cinema] = [str(x) for x in result["dates"][town][cinema]]

        return result

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
        self.dates[town][cinema_name].sort()

    def merge(self, other):
        self.details.merge(other.details)

        for town in other.dates:
            for cinema in other.dates[town]:
                self.add_dates(cinema, town, other.dates[town][cinema])

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
        for town in self.dates:
            for cinema in self.dates[town]:
                self_cinemas.append(cinema)

        other_cinemas = []
        for town in other.dates:
            for cinema in other.dates[town]:
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
            # print("MERGING", self.name, other.name)

            if self._same_cinema_heuristic(other) and fuzzy_score_partial < 85:
                # print(f"NOT MERGING SAME {self.name}, {other.name}")
                pass
            elif fuzzy_score_partial < 90 and fuzzy_score < 50:
                # print(f"NOT MERGING FUZZY {self.name}, {other.name}")
                pass
            else:
                result = True

        if not result and self._without_language_name_heuristic(self.name, other.name):
            # logger.debug(f"Merging with new heuristic {self.name}, {other.name}")
            result = True

        if result and self.details.length and other.details.length:
            if abs(self.details.length - other.details.length) > FILM_LENGTH_VARIANCE:
                # print(f"Not identical, legnths too far apart #1 {self.name}, #2 {other.name}")
                result = False
        if result and self.details.year and other.details.year:
            if abs(self.details.year - other.details.year) > FILM_YEAR_VARIANCE:
                # print(f"Not identical, years differ #1 {self.name}, #2 {other.name}, {self.details.year}, {other.details.year}")
                result = False

        # if result:
        #     print(f"MERGING {self.name} | {other.name} | {fuzzy_score_partial} | {fuzzy_score} | {self.details.length} | {other.details.length}")

        return result

    def get_screenings_on_date(self, date, hour_filter=False):
        dates = dict()
        for town in self.dates:
            for cinema in self.dates[town]:
                for d in self.dates[town][cinema]:
                    if same_date(d, date):
                        if hour_filter:
                            d_minutes = d.hour * 60 + d.minute
                            date_minutes = date.hour * 60 + date.minute
                            if d_minutes < date_minutes:
                                continue
                        if not cinema in dates:
                            dates[cinema] = [d]
                        else:
                            dates[cinema].append(d)
        return dates
    
    def has_screenings_on_date(self, date):
        for town in self.dates:
            for cinema in self.dates[town]:
                for d in self.dates[town][cinema]:
                    if same_date(d, date):
                        return True

        return False
