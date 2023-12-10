import time
import requests
import datetime
import urllib.parse
import json
import re
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class CinemathequeCinema(Cinema):
    NAME = "Cinematheque"
    TOWNS = ["Tel Aviv"]
    BASE_URL = "https://www.cinema.co.il/shown/?date={0}-{1}-{2}"
    DATE_FORMAT = "%d.%m"
    HOUR_PATTERN = "\d\d:\d\d"
    UPDATE_INTERVAL = 60 * 60

    def __init__(self):
        super().__init__()

    def get_films_by_date(self, date, town):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
        response = requests.get(self.BASE_URL.format(date.year, date.month, date.day), headers=headers)
        response.encoding = "utf-8"

        html = BeautifulSoup(response.text, "html.parser")
        shown_content_movie_element = html.find("div", {"class": "shown-content-movie"})
        grid_boxes = shown_content_movie_element.find_all("div", {"class": "festival-grid-box"})

        films = []
        for grid_box in grid_boxes:
            title = grid_box.find("div", {"class": "title"})

            name = title.h3.a.text
            link = title.h3.a["href"]
            basic_details = title.p.text.strip()

            films.append(Film(name))

            img_wrapper = grid_box.find("div", {"class": "img-wraper"})
            films[-1].set_image_url(img_wrapper.img["data-src"])

            time_span = grid_box.find("span", {"class": "time"})
            hour, minute = time_span.text.split(":")
            film_date = datetime.datetime(date.year, date.month, date.day, int(hour), int(minute))
            films[-1].add_dates(self.NAME, town, [film_date])

            films[-1].add_link(self.NAME, link)

            paragraph = grid_box.find("div", {"class": "paragraph"})
            description = paragraph.p.text
            films[-1].details.description = description

            h4 = paragraph.find_all("h4")
            if len(h4) == 2:
                director = h4[0].text.split(":")[1]
                films[-1].details.director = director

                language = h4[1].text.split(":")[1]
                films[-1].details.language = language

            basic_details = basic_details.split(" / ")
            for detail in basic_details:
                detail = detail.strip()
                if detail.isnumeric():
                    films[-1].details.year = int(detail)
                elif "אורך" in detail:
                    films[-1].details.length = int(detail.split(":")[1])
                else:
                    films[-1].details.countries = detail
            
        self._merge_films(films)

        return films

    def get_film_details(self, film):
        return None

    def get_provided_film_details(self):
        return []
