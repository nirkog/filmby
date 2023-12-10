import time
import requests
import datetime
import urllib.parse
import json
import re
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class JaffaCinema(Cinema):
    NAME = "Jaffa"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://www.jaffacinema.com/"
    DATE_FORMAT = "%d/%m/%y"
    HOUR_FORMAT = "%H:%M"
    UPDATE_INTERVAL = 60 * 60
    DATE_PATTERN = "\d\d/\d\d"
    HOUR_PATTERN = "\d\d:\d\d"

    def __init__(self):
        super().__init__()
        self.films = self.get_films()
        self.last_update = time.time()

    def get_date_from_option(self, text):
        date = re.findall(self.DATE_PATTERN, text)
        hour = re.findall(self.HOUR_PATTERN, text)

        if len(date) == 0:
            return None
        else:
            day, month = [int(x) for x in date[0].split("/")]

        if len(hour) > 0:
            hour, minute = [int(x) for x in hour[0].split(":")]
        else:
            hour = minute = 0

        result = datetime.datetime(datetime.datetime.today().year, month, day, hour, day)

        return result
    
    def parse_length(self, text):
        text = "".join([x for x in text if x in " 0123456789"])
        parts = [x for x in text.split(" ") if x != ""]
        hours = int(parts[0])

        if len(parts) > 1:
            minutes = int(parts[1])
        else:
            minutes = 0

        return hours * 60 + minutes

    def get_films(self):
        response = requests.get(self.BASE_URL)
        html = BeautifulSoup(response.text, "html.parser")
        screenings = html.find("div", {"id": "screenings"})

        films = []
        for screening in screenings.children:
            name = screening.div.div.div.h2.text
            image = screening.div.div.img["src"]
            link = self.BASE_URL
            
            dates_select = screening.find("select")
            if dates_select != None:
                date_options = dates_select.find("option")
                date_options = [option.text for option in date_options]
                dates = [self.get_date_from_option(option) for option in date_options]
                dates = [x for x in dates if x != None]
            else:
                date_text = screening.find("div", {"class": "date-btn"}).p.text
                dates = [self.get_date_from_option(date_text)]

            in_parent = screening.find("div", {"class": "in-parent"}) 
            paragraphs = in_parent.find_all("p")
            try:
                countries, year = paragraphs[0].text.split(" / ")
            except Exception:
                continue
            countries = countries.split(", ")
            year = int(year)

            if len(paragraphs) > 1:
                description = paragraphs[1].text
            else:
                description = in_parent.find("span").text

            info_title = screening.find("div", {"class": "info-title"})
            length, director = info_title.p.text.split(" | ")
            length = self.parse_length(length)
            
            films.append(Film(name))
            films[-1].set_image_url(image)
            films[-1].add_dates(self.NAME, self.TOWNS[0], dates)
            films[-1].add_link(self.NAME, link)
            films[-1].details.countreis = countries
            films[-1].details.length = length
            films[-1].details.director = director
            films[-1].details.description = description
            films[-1].details.year = year

        return films

    def get_films_by_date(self, date, town):
        if time.time() - self.last_update > self.UPDATE_INTERVAL:
            self.films = self.get_films()

        films = []
        for film in self.films:
            film_dates = film.dates[self.TOWNS[0]][self.NAME]
            for film_date in film_dates:
                if film_date.year == date.year and film_date.month == date.month and film_date.day == date.day:
                    films.append(film)

        return films
           
    def get_film_details(self, film):
        return None

    def get_provided_film_details(self):
        return []
