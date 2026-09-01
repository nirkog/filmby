import time
import requests
import datetime
import urllib.parse
import json
import re
from loguru import logger
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class JaffaCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע יפו"}
    NAME = "Jaffa"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://www.jaffacinema.com/"
    UPDATE_INTERVAL = 60 * 60
    DATE_FORMAT = "%Y/%d/%mT%H:%M"

    def __init__(self):
        super().__init__()
        self.films = self.get_films()

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
        screenings = html.find_all("article", {"class": "jaffa-movie-card"})

        films = []
        for screening in screenings:
            try:
                name = screening.find("h2").text
                image = screening.find("img")["src"]
                link = screening.find("a", {"class": "jaffa-movie-card__screening"})["href"]

                dates = []
                date_elements = screening.find_all("span", {"class": "jaffa-movie-card__date-link"})
                for element in date_elements:
                    date_parts = "".join([c for c in element.text if c in "0123456789/: "])
                    date_parts = date_parts.split(" ")
                    date_parts = [x for x in date_parts if x != ""]
                    assert len(date_parts) == 2
                    hour_text = None
                    date_text = None
                    for part in date_parts:
                        if "/" in part:
                            date_text = part
                        elif ":" in part:
                            hour_text = part
                    year = str(datetime.datetime.now().year)
                    full_date_text = year + "/" + date_text + "T" + hour_text
                    dates.append(datetime.datetime.strptime(full_date_text, self.DATE_FORMAT))

                description_element = screening.find("div", {"class": "jaffa-movie-card__desc-inner"}) 
                paragraphs = description_element.find_all("p")
                countries = None
                year = None
                countries_year_raw_str = paragraphs[0].text

                if "/" in countries_year_raw_str:
                    countries, year = countries_year_raw_str.split("/")[:2]
                    countries = countries.split(", ")
                elif "|" in countries_year_raw_str:
                    countries, year = countries_year_raw_str.split("|")[:2]
                    countries = countries.split(", ")
                else:
                    logger.warning(f"Could not parse countries and year for film {name} (string was \"{countries_year_raw_str}\")")

                try:
                    year = int(year.strip().replace(" ", "")[:4])
                    assert year > 1900 and year < 2100
                except Exception as e:
                    logger.warning(f"Could not parse year for film {name} (string was \"{year}\"), error: {str(e)}")
                    year = None

                try:
                    description = ""
                    elements = description_element.find_all("p") + description_element.find_all("span")
                    for element in elements:
                        if element.text == countries_year_raw_str:
                            continue

                        description += element.text + "<br>"
                    description = description[:-4]
                except Exception as e:
                    logger.warning(f"Could not parse description for film {name}, error: {str(e)}")
                    description = None

                # TODO: Add director and length
                
                films.append(Film(name))
                films[-1].set_image_url(image)
                films[-1].add_dates(self.NAME, self.TOWNS[0], dates)
                films[-1].add_link(self.NAME, link)
                # films[-1].details.length = length
                # films[-1].details.director = director
                films[-1].details.countries = countries
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
