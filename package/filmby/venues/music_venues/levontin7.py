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

class Levontin7(MusicVenue):
    TRANSLATED_NAMES = {"heb": "לבונטין 7"}
    NAME = "Levontin7"
    MONTHS = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }
    HEADERS = {
        "Host": "levontin7.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "https://levontin7.com/timetable-event/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0"
    }
    TIMETABLE_URL = "https://levontin7.com/wp-admin/admin-ajax.php?action=fat_event_get_timetable&sc_id=952&sc_category=&sc_organizer=&month={0}&year={1}&view=listDay"
    GRID_URL = "https://levontin7.com/wp-admin/admin-ajax.php?action=fat_event_filter&sc_id=931&current_page={0}&layout=grid"
    EVENT_DETAILS_URL = "https://levontin7.com/wp-admin/admin-ajax.php?action=fat_event_get_event_detail&id={0}"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        super().__init__()

        self._concerts = self._get_concerts()

    def _concert_raw_concert_to_concert(self, raw_concert):
        start_date = datetime.datetime.strptime(raw_concert["start_date"], self.DATE_FORMAT) 
        event_details_raw = requests.get(self.EVENT_DETAILS_URL.format(raw_concert["id"]), self.HEADERS)
        event_details = event_details_raw.json()

        concert = Concert(raw_concert["title"])
        concert.set_image_url(event_details["thumb"])
        concert.add_link(self.NAME, raw_concert["url"])
        concert.add_dates(self.NAME, [start_date])

        description_parts = []
        description_html = BeautifulSoup(event_details["content"], "html.parser")
        elements = list(description_html.children)
        while len(elements) > 0:
            element = elements.pop(0)
            if type(element) == bs4.element.NavigableString:
                if str(element) != None:
                    description_parts.append(str(element))
                continue

            has_children = False
            for i, child in enumerate(element.children):
                elements.insert(i, child)
                has_children = True

            if not has_children:
                if element.innerHTML != None:
                    description_parts.append(element.innerHTML)

        concert.details.description = "".join(description_parts)
        concert.details.description = concert.details.description.replace("\n", "<br>")
        concert.details.doors = start_date

        self._thread_concerts.append(concert)

    def _get_concerts(self):
        start = time.time()
        current_date = datetime.datetime.now()
        month_name = self.MONTHS[current_date.month]
        year = current_date.year
        formatted_url = self.TIMETABLE_URL.format(month_name, year)
        response = requests.get(formatted_url, headers=self.HEADERS)
        concerts_raw = response.json()

        concerts = []
        threads = []
        self._thread_concerts = []
        for raw_concert in concerts_raw:
            start_date = datetime.datetime.strptime(raw_concert["start_date"], self.DATE_FORMAT) 
            if start_date < current_date:
                continue

            threads.append(threading.Thread(target=self._concert_raw_concert_to_concert, args=(raw_concert,)))
            threads[-1].start()

            time.sleep(0.05)

        for thread in threads:
            thread.join()

        return self._thread_concerts

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
