import requests
import datetime
import urllib.parse
import parse
import json
import bs4
import time
import threading
from bs4 import BeautifulSoup
from loguru import logger

from filmby.venues.music_venue import MusicVenue
from filmby.events.concert import Concert, ConcertDetails

class Barby(MusicVenue):
    TRANSLATED_NAMES = {"heb": "בארבי"}
    NAME = "Barby"
    HEADERS = {
        "Host": "barby.co.il",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-GPC": "1",
        "Alt-Used": "barby.co.il",
        "Connection": "keep-alive",
        "Referer": "https://barby.co.il/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }
    BASE_API_URL = "https://barby.co.il/api/"
    FIND_SHOWS_API_URL = BASE_API_URL + "shows/find"
    IMAGE_BASE_URL = "https://images.barby.co.il/Logos/"
    SHOW_BASE_URL = "https://barby.co.il/show/"
    DATE_FORMAT = "%d/%m/%Y %H:%M"

    def __init__(self):
        super().__init__()

        self._concerts = self._get_concerts()

    def _get_concerts(self):
        response = requests.get(self.FIND_SHOWS_API_URL, headers=self.HEADERS)
        shows = response.json()["returnShow"]["show"]

        concerts = []
        for show in shows:
            concert = Concert(show["showName"])
            concert.set_image_url(self.IMAGE_BASE_URL + show["showImage"])
            concert.add_link(self.NAME, self.SHOW_BASE_URL + show["showId"])

            date = datetime.datetime.strptime(show["showDate"] + " " + show["showTime"], self.DATE_FORMAT)
            concert.add_dates(self.NAME, [date])

            concert.details.description = show["showTitle"]
            concert.details.doors = date

            concerts.append(concert)

        return concerts

    def get_events_by_date(self, date):
        result = []

        for concert in self._concerts:
            for concert_date in concert.dates[self.NAME]:
                if concert_date.year == date.year and concert_date.month == date.month and concert_date.day == date.day:
                    result.append(concert)
                    break

        return result

    def get_event_details(self, film):
        pass
        
    def get_provided_event_details(self):
        return []
