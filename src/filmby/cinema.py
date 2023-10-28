class Cinema:
    NAME = None
    TOWNS = None # TODO: Make this dynamic???

    def __init__(self, town):
        self.town = town

    def get_films_by_date(self, date):
        pass

    def _merege_films(self, films):
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
