from filmby.events.film import Film, FilmDetails
from filmby.venues.cinema import Cinema

class JaffaHillCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע הפסגה"}
    NAME = "Jaffa Hill"
    TOWNS = ["Tel Aviv"]

    def __init__(self):
        pass

    def get_films_by_date(self, date, town):
        return []
    
    def get_film_details(self, film):
        return None

    def get_provided_film_details(self):
        return []
