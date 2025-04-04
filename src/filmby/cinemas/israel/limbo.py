import time
import requests
import datetime
import urllib.parse
import json
import re
import emoji
from bs4 import BeautifulSoup
from loguru import logger

from ...cinema import Cinema
from ...film import Film

class LimboCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "קולנוע לימבו"}
    NAME = "Limbo"
    TOWNS = ["Tel Aviv"]
    # BASE_URL = "https://www.hameretz2.org/limbo"
    BASE_URL = "https://test.hameretz2.org/"
    DATE_FORMAT = "%H:%M"
    NEW_DATE_FORMAT = "%d.%m"
    UPDATE_INTERVAL = 60 * 60
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    HEBREW_MONTHS = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]

    def __init__(self):
        super().__init__()

        self.films = self.get_films()
        self.last_update = time.time()

    def get_films(self):
        response = requests.get(self.BASE_URL, headers=self.HEADERS)
        response.encoding = "utf-8"

        html = BeautifulSoup(response.text, "html.parser")
        list_items = html.find_all("a", {"class": "zygo-event-card"})

        films = []
        for list_item in list_items:
            if not "filter-%d7%9c%d7%99%d7%9e%d7%91%d7%95" in list_item['class']:
                continue
            # print("HI")
            image_url = list_item.find("img")["src"]
            # name = list_item.find("div", {"class": "event-title"}).text
            name = list_item.find(class_="event-title").text
            # print("HI2")
            name = emoji.replace_emoji(name)
            if name.endswith("קולנוע לימבו"):
                name = name[:-len("קולנוע לימבו")]
            if name.endswith("לימבו"):
                name = name[:-len("לימבו")]
            name = name.strip()

            films.append(Film(name))

            link = list_item["href"]
            films[-1].add_link(self.NAME, link)

            # image_url = image_url[:image_url.find(".png") + 4]
            films[-1].set_image_url(image_url) 

            # date = list_item.find("div", {"data-hook": "date"}).text
            # print("HI3")
            # date, hour = date.split(",")[:2]

            # hour = hour.strip()[:5]
            # hour = datetime.datetime.strptime(hour, self.DATE_FORMAT)
            # 
            # date = date.strip()
            # day, month, year = date.split(" ")
            # year = int(year)
            # day = int(day)
            # 
            # for i, name in enumerate(self.HEBREW_MONTHS):
            #     if name in month:
            #         month = i + 1
            #         break
            # else:
            #     month = 1


            # date = datetime.datetime(year, month, day, hour.hour, hour.minute) 
            date = list_item.find("div", {"class": "event-datetime"}).text
            date = datetime.datetime.strptime(date, self.NEW_DATE_FORMAT)
            date = datetime.datetime(datetime.datetime.now().year, date.month, date.day, 19)
            # print("DATE", date)
            films[-1].add_dates(self.NAME, self.TOWNS[0], [date])

            description = list_item.find("div", {"class": "event-summary"}).text
            description = "שימו לב! השעות של הסרטים בקולנוע לימבו לא מדויקות, גשו ללינק שמופיע גדי לקבל את השעה המדויקת.<br>" + description
            # print("HI4")
            films[-1].details.description = description

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
