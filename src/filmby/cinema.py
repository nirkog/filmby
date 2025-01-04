from abc import ABC, abstractmethod

class Cinema(ABC):
    TRANSLATED_NAMES = None
    NAME = None
    TOWNS = None # TODO: Make this dynamic???

    def __init__(self):
        self.details_cache = dict()

    def _add_to_details_cache(self, film, details):
        self.details_cache[film.links[self.NAME]] = details

    def _get_details_from_cache(self, film):
        if self.NAME in film.links:
            if film.links[self.NAME] in self.details_cache:
                return self.details_cache[film.links[self.NAME]] 
        return None

    @abstractmethod
    def get_films_by_date(self, date):
        pass
    
    @abstractmethod
    def get_film_details(self, film):
        pass
    
    @abstractmethod
    def get_provided_film_details(self):
        pass

    def _merge_films(self, films):
        i = 0
        found_names = dict()
        while i < len(films):
            film = films[i]
            if film.name in found_names:
                films[found_names[film.name]].merge(film)
                films.remove(film)
            else:
                found_names[film.name] = i
                i += 1

    def clean_cache(self):
        self.details_cache = dict()
