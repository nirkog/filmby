#!/usr/bin/python3

import sys
sys.path.append("./src/")

import os
import pickle
import datetime

from filmby.film import Film
from filmby import CINEMAS

def main():
    if len(sys.argv) < 2:
        print("Usage: ./add_film.py <film-pickle-db-path>")
        return

    film_db_path = sys.argv[1]

    if not os.path.exists(film_db_path):
        with open(film_db_path, "wb") as f:
            pickle.dump([], f)
    
    with open(film_db_path, "rb") as f:
        film_db = pickle.load(f)

    name = input("Enter film name: ")
    image_url = input("Enter image url: ")

    film = Film(name)
    film.image_url = image_url

    cinema_names = []
    for cinema in CINEMAS["Israel"]:
        cinema_names.append(cinema.NAME)

    print("Please enter the film links and dates, first the cinema name, and then the link and dates")
    print("Date format is D.M.Y h:m")
    date_format = "%d.%m.%Y %H:%M"
    while True:
        cinema_name = input("Enter cinema name (enter blank line to stop): ")
        if cinema_name == "":
            break

        if not cinema_name in cinema_names:
            print("Unknown cinema, ignoring")
            continue

        link = input("Enter film link: ")
        film.add_link(cinema_name, link)

        dates = []
        while True:
            date_string = input("Enter date (enter blank line to stop): ")
            if date_string == "":
                break
            date = datetime.datetime.strptime(date_string, date_format)
            dates.append(date)

        film.add_dates(cinema_name, "Tel Aviv", dates)

    film.details.description = input("Enter film description: ")
    film.details.director = input("Enter film director: ")
    cast = input("Enter film cast (separated by commas): ")
    film.details.cast = [x.strip() for x in cast.split(",")]
    film.details.length = int(input("Enter film length (in minutes): "))
    countries = input("Enter film countries (separated by commas): ")
    film.details.countries = [x.strip() for x in countries.split(",")]
    film.details.language = input("Enter film language: ")
    film.details.year = int(input("Enter film year: "))

    film_db.append(film)

    with open(film_db_path, "wb") as f:
        pickle.dump(film_db, f)

    print(f"Added film successfully! There are now {len(film_db)} files in the DB")

if __name__ == "__main__":
    main()
