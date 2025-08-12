import requests
import datetime
import os
import re
import time
from loguru import logger

from ...cinema import Cinema
from ...film import Film

HEADERS = {
    "x-ig-app-id": "936619743392459",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}
URL = "https://www.instagram.com/api/v1/users/web_profile_info/?username=old_jaffa"

class JaffaHillCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע הפסגה"}
    NAME = "Jaffa Hill"
    TOWNS = ["Tel Aviv"]
    UPDATE_INTERVAL = 60 * 60 * 3
    DATE_FORMAT = "%d.%m"

    def __init__(self):
        super().__init__()

        self.last_update = time.time()
        self.films = self.get_films()

    def get_films(self):
        response = requests.get(URL, headers=HEADERS)
        if response.status_code != 200:
            logger.warning(f"Instagram request failed")
            return []

        data = response.json()
        films = []

        posts = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
        for post in posts:
            post_data = post["node"]
            shortcode = post_data["shortcode"]
            caption = post_data["edge_media_to_caption"]["edges"][0]["node"]["text"]
            image_url = post_data["display_url"]

            if "קולנוע" in caption and caption.count("👈") > 1:
                lines = caption.splitlines()
                for i, line in enumerate(lines):
                    if not "👈" in line:
                        continue

                    try:
                        description = lines[i + 1]
                        date = re.search(r"\s(\d{1,2}?\.\d{1,2})\s", line).groups()[0]
                        date = datetime.datetime.strptime(date, self.DATE_FORMAT)
                        date = date.replace(year=datetime.datetime.now().year)
                        date = date.replace(hour=21)
                        date = date.replace(minute=0)
                        name = re.search(r"–\s(.+)\s\|", line).groups()[0]
                        url = f"https://instagram.com/p/{shortcode}/"
                        films.append(Film(name))
                        films[-1].details.description = description
                        films[-1].add_dates(self.NAME, "Tel Aviv", [date])
                        films[-1].add_link(self.NAME, url)
                        films[-1].set_image_url(image_url)
                    except Exception as e:
                        # logger.warning(f"Failed addi
                        pass

        self.last_update = time.time()

        return films

    def get_films_by_date(self, date, town):
        if time.time() - self.last_update > self.UPDATE_INTERVAL:
            self.films = self.get_films()

        films = []
        for film in self.films:
            if film.has_screenings_on_date(date):
                films.append(film)

        return films
    
    def get_film_details(self, film):
        return None

    def get_provided_film_details(self):
        return []
