import requests
import datetime
import urllib.parse
import json
from bs4 import BeautifulSoup
from loguru import logger

from ...cinema import Cinema
from ...film import Film, FilmDetails

class CinemaCityCinema(Cinema):
    TRANSLATED_NAMES = {"heb": "סינמה סיטי"}
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
        self.film_ids, self.film_details = self.get_movie_ids_and_details() # TODO: Move this to get_films_by_date

    def get_movie_ids_and_details(self):
        response = requests.get(self.MOVIES_URL)
        html = BeautifulSoup(response.text, "html.parser")
        movies = html.find_all("div", {"class": "movie-thumb"})
        ids = dict()
        details_dict = dict()

        for movie in movies:
            try:
                movie_id = movie["data-linkmobile"][7:]
                children = movie.find(recursive=True)
                title = children.find("h4", {"class": "title"}).text

                ids[title] = movie_id

                details = FilmDetails()
                description_element = movie.find("p", {"class": "flip_content"})
                details.description = description_element.text

                flipcontent = movie.find("div", {"class": "flipcontent"})
                for child in flipcontent.children:
                    if "אורך" in child.text:
                        span = child.find("span")
                        details.length = int(span.text)

                details_dict[movie_id] = details
            except Exception as e:
                logger.error(f"Failed to parse film, error: {str(e)}")
        
        return ids, details_dict

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

        for film in json_films:
            try:
                name = film["Name"]
                film_id = self.film_ids[film['Name']]
                clean_name = name.replace("-מדובב", "") # TODO: Change???
                films.append(Film(clean_name))
                 
                encoded_pic_name = urllib.parse.quote(film["Pic"])
                films[-1].set_image_url(self.IMAGE_URL.format(encoded_pic_name, 300, 300))

                date = datetime.datetime.strptime(film["Dates"]["Date"], self.FILM_DATE_FORMAT)
                films[-1].add_dates(self.NAME, town, [date])

                films[-1].add_link(self.NAME, self.BASE_URL + f"movie/{film_id}")
                films[-1].details = self.film_details[film_id]
            except Exception as e:
                logger.error(f"Failed to add film, error: {str(e)}")

        self._merge_films(films)

        return films

    def get_film_details(self, film):
        pass

    def get_provided_film_details(self):
        return []
