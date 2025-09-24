import time
import requests
import datetime
import urllib.parse
import json
import re
from loguru import logger
from bs4 import BeautifulSoup

from filmby.events.film import Film, FilmDetails
from filmby.venues.cinema import Cinema

class JaffaCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע יפו"}
    NAME = "Jaffa"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://www.jaffacinema.com/"
    UPDATE_INTERVAL = 60 * 60
    DATE_PATTERN = "\\d\\d/\\d\\d"
    HOUR_PATTERN = "\\d\\d:\\d\\d"

    def __init__(self):
        super().__init__()
        self.films = self.get_films()

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

        result = datetime.datetime(datetime.datetime.today().year, month, day, hour, minute)

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
            try:
                name = screening.div.div.div.h2.text
                image = screening.div.div.img["src"]
                link = self.BASE_URL
                
                dates_select = screening.find("select")
                if dates_select != None:
                    date_options = dates_select.find_all("option")
                    date_options = [option.text for option in date_options]
                    dates = [self.get_date_from_option(option) for option in date_options]
                    dates = [x for x in dates if x != None]
                else:
                    date_text = screening.find("div", {"class": "date-btn"}).p.text
                    dates = [self.get_date_from_option(date_text)]

                in_parent = screening.find("div", {"class": "in-parent"}) 
                paragraphs = in_parent.find_all("p")
                countries = None
                year = None
                try:
                    raw_str = list(in_parent.children)[0].text
                    countries, year = raw_str.split("/")
                    countries = countries.split(", ")
                except Exception as e:
                    logger.warning(f"Could not parse countries and year for film {name} (string was \"{raw_str}\"), error: {str(e)}")
                    countries = None

                try:
                    year = int(year.strip().replace(" ", "")[:4])
                    assert year > 1900 and year < 2100
                except Exception as e:
                    logger.warning(f"Could not parse year for film {name} (string was \"{year}\"), error: {str(e)}")
                    year = None

                try:
                    description = ""
                    elements = in_parent.find_all("p") + in_parent.find_all("span")
                    for element in elements:
                        if element.text == raw_str:
                            continue

                        description += element.text + "<br>"
                    description = description[:-4]
                except Exception as e:
                    logger.warning(f"Could not parse description for film {name}, error: {str(e)}")
                    description = None

                info_title = screening.find("div", {"class": "info-title"})
                length, director = info_title.p.text.split(" | ")
                length = self.parse_length(length)
                
                films.append(Film(name))
                films[-1].set_image_url(image)
                films[-1].add_dates(self.NAME, self.TOWNS[0], dates)
                films[-1].add_link(self.NAME, link)
                films[-1].details.countries = countries
                films[-1].details.length = length
                films[-1].details.director = director
                films[-1].details.description = description
                films[-1].details.year = year
            except Exception as e:
                logger.error(f"Could not parse screening, error: {str(e)}")

        self.last_update = time.time()

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
