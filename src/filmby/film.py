import requests
import os

CONTENT_TYPES_TO_FILE_ENGINGS = {
    "image/jpeg": ".jpg"
}

class Film:
    def __init__(self, name):
        self.name = name
        self.image_url = None
        self.dates = dict()
        self.links = dict()

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

    def add_dates(self, cinema_name, dates):
        if not cinema_name in self.dates:
            self.dates[cinema_name] = dates
        else:
            self.dates[cinema_name].extend(dates)

        self.dates[cinema_name] = list(set(self.dates[cinema_name]))

    def merge(self, other):
        if not self.image_url:
            self.image_url = other.image_url

        for cinema in other.dates:
            self.add_dates(cinema, other.dates[cinema])

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
