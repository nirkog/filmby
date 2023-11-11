import requests
import os

CONTENT_TYPES_TO_FILE_ENGINGS = {
    "image/jpeg": ".jpg"
}

# TODO: Add cachable and non-cachable properties (should receive cache in get_films and only update non-cachable properties)
# TODO: Add description
# TODO: Add extra details (length, director, etc.)
# TODO: Support dubbed films

def same_date(first, second):
    return (first.year == second.year) and (first.month == second.month) and (first.day == second.day)

class Film:
    def __init__(self, name):
        self.name = name
        self.image_url = None
        self.dates = dict()
        self.links = dict()
        self.description = ""

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
        if not self.image_url:
            self.image_url = other.image_url

        for town in other.dates:
            for cinema in other.dates[town]:
                self.add_dates(cinema, town, other.dates[town][cinema])

        for cinema in other.links:
            if not cinema in self.links:
                self.links[cinema] = other.links[cinema]

    def have_same_name(self, other):
        if self.name == other.name:
            return True

        # TODO: Maybe needs improvement
        
        if self.name.replace("-", "") == other.name.replace("-", ""):
            return True
        
        if self.name.replace("-", " ") == other.name.replace("-", " "):
            return True

        return False
    
    def has_screenings_on_date(self, date):
        for town in self.dates:
            for cinema in self.dates[town]:
                for d in self.dates[town][cinema]:
                    if same_date(d, date):
                        return True

        return False
