import time
import requests
import datetime
import emoji
from bs4 import BeautifulSoup
from loguru import logger

from filmby.events.concert import Concert
from filmby.events.party import Party
from filmby.events.show import Show
from filmby.event import Event
from filmby.venue import Venue

class Hameretz2(Venue):
    TRANSLATED_NAMES = {"heb": "המרץ 2"}
    NAME = "Hameretz2"
    BASE_URL = "https://hameretz2.org/"
    DATE_FORMAT = "%H:%M"
    NEW_DATE_FORMAT = "%d.%m"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    def __init__(self):
        super().__init__()

        self.events = self.get_events()

    def get_events(self):
        response = requests.get(self.BASE_URL, headers=self.HEADERS)
        response.encoding = "utf-8"

        html = BeautifulSoup(response.text, "html.parser")
        list_items = html.find_all("a", {"class": "zygo-event-card"})

        events = []
        for list_item in list_items:
            name = list_item.find(class_="event-title").text
            name = emoji.replace_emoji(name)
            if name.endswith("קולנוע לימבו"):
                name = name[:-len("קולנוע לימבו")]
            if name.endswith("לימבו"):
                name = name[:-len("לימבו")]
            name = name.strip()

            # Skip movies
            if "filter-%d7%9c%d7%99%d7%9e%d7%91%d7%95" in list_item['class']: 
                continue

            if "filter-%d7%9c%d7%99%d7%99%d7%91" in list_item['class']:
                event = Concert(name)
            elif "filter-%d7%9c%d7%99%d7%9c%d7%94" in list_item['class']:
                event = Party(name)
            elif "filter-%d7%9e%d7%95%d7%a4%d7%a2" in list_item['class']:
                event = Show(name)
            else:
                event = Event(name)

            link = list_item["href"]
            event.add_link(self.NAME, link)

            image_url = list_item.find("img")["src"]
            event.set_image_url(image_url) 

            date = list_item.find("div", {"class": "event-datetime"}).text
            date = datetime.datetime.strptime(date, self.NEW_DATE_FORMAT)
            date = datetime.datetime(datetime.datetime.now().year, date.month, date.day, 19)
            event.add_dates(self.NAME, [date])

            if type(event) == Concert:
                event.details.doors = date

            description = list_item.find("div", {"class": "event-summary"}).text
            description = "<span class=\"limbo-comment\">שימו לב! האירועים של הסרטים במרץ 2 לא מדויקות, גשו ללינק שמופיע גדי לקבל את השעה המדויקת.</span><br><br>" + description
            event.details.description = description

            events.append(event)

        return events

    def get_events_by_date(self, date):
        events = []
        for event in self.events:
            event_dates = event.dates[self.NAME]
            for event_date in event_dates:
                if event_date.year == date.year and event_date.month == date.month and event_date.day == date.day:
                    events.append(event)

        return events

    def get_event_details(self, event):
        return None

    def get_provided_event_details(self):
        return []
