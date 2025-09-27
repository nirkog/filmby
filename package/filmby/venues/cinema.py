from abc import ABC, abstractmethod

from filmby.venue import Venue

class Cinema(Venue):
    def __init__(self):
        super().__init__()

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
