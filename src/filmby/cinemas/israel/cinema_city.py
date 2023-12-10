import requests
import datetime
import urllib.parse
import json
from bs4 import BeautifulSoup

from ...cinema import Cinema
from ...film import Film

class CinemaCityCinema(Cinema):
    NAME = "Cinema City"
    TOWNS = ["Tel Aviv", "Rishon", "Jerusalem", "Kfar Saba", "Beer Sheva", "Ashdod", "Hedera", "Netanya"]
    THEATER_IDS = {
                "Tel Aviv": 1,
                "Rishon": 2,
                "Jerusalem": 3,
                "Kfar Saba": 4,
                "Netanya": 5,
                "Beer Sheva": 17,
                "Hedera": 13,
                "Ashdod": 25
            }
    TIX_THEATER_IDS = {
                "Tel Aviv": 1170,
                "Rishon": 1173,
                "Jerusalem": 1174,
                "Kfar Saba": 1175,
                "Netanya": 1176,
                "Beer Sheva": 1178,
                "Hedera": 1350,
                "Ashdod": 1181
            }
    BASE_URL = "https://www.cinema-city.co.il/"
    DATES_URL = "tickets/GetDatesByTheater?theaterId={0}"
    FILMS_URL = "tickets/EventsFlat?TheatreId={0}&VenueTypeId=0&date={1}"
    IMAGE_URL = "https://www.cinema-city.co.il/images/{0}?w={1}&h={2}"
    MOVIES_URL = "https://www.cinema-city.co.il/movies/"
    DATE_FORMAT = "%d/%m/%Y"
    FILM_DATE_FORMAT = "%d/%m/%Y %H:%M"

    def __init__(self):
        super().__init__()
        self.film_ids = self.get_movie_ids() # TODO: Move this to get_films_by_date

    def get_movie_ids(self):
        response = requests.get(self.MOVIES_URL)
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("div", {"class": "movie-thumb"})
        ids = dict()

        for movie in movies:
            movie_id = movie["data-linkmobile"][7:]
            children = movie.find(recursive=True)
            title = children.find("h4", {"class": "title"}).text

            ids[title] = movie_id

        return ids

    def get_films_by_date(self, date, town):
        theater_id = self.THEATER_IDS[town]
        tix_theater_id = self.TIX_THEATER_IDS[town]
        request = requests.get(self.BASE_URL + self.DATES_URL.format(theater_id))
        dates = eval(request.text)
        original_dates = eval(request.text)
        dates = ["".join([c for c in date if c in "0123456789/"]) for date in dates]
        dates = [datetime.datetime.strptime(date, self.DATE_FORMAT) for date in dates]
        dates = [i for i, d in enumerate(dates) if ((d.day == date.day) and (d.month == date.month) and (d.year == date.year))]
        
        if len(dates) == 0:
            return None

        date_index = dates[0]
        encoded_date = urllib.parse.quote(original_dates[date_index], safe="")

        request = requests.get(self.BASE_URL + self.FILMS_URL.format(tix_theater_id, encoded_date))
        json_films = json.loads(request.text)
        films = []

        # TODO: Merge duplicates
        for film in json_films:
            name = film["Name"]
            clean_name = name.replace("-מדובב", "") # ???
            films.append(Film(clean_name))
             
            encoded_pic_name = urllib.parse.quote(film["Pic"])
            films[-1].set_image_url(self.IMAGE_URL.format(encoded_pic_name, 300, 300))

            date = datetime.datetime.strptime(film["Dates"]["Date"], self.FILM_DATE_FORMAT)
            films[-1].add_dates(self.NAME, town, [date])

            films[-1].add_link(self.NAME, self.BASE_URL + f"movie/{self.film_ids[film['Name']]}")

        self._merge_films(films)

        return films

    def get_film_details(self, film):
        pass

    def get_provided_film_details(self):
        return []
