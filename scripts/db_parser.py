#!/usr/bin/python3

import sys
sys.path.append("./src/")

import pickle

def main():
    if len(sys.argv) < 2:
        print("Usage: ./add_film.py <film-pickle-db-path>")
        return

    film_db_path = sys.argv[1]
    with open(film_db_path, "rb") as f:
        film_db = pickle.load(f)

    print(f"There are {len(film_db)} films in the DB\n")

    for film in film_db:
        print("=" * 30 + "\n")
        print(f"Film name: {film.name}")
        print(f"Image URL: {film.image_url}")

        for cinema_name in film.links:
            print(f"Link for {cinema_name}: {film.links[cinema_name]}")

        print("Film details:")
        print(f"\tDescription: {film.details.description}")
        print(f"\tDirector: {film.details.director}")
        print(f"\tCast: {', '.join(film.details.cast) if film.details.cast != None else None}")
        print(f"\tLength: {film.details.length} minutes")
        print(f"\tCountries: {', '.join(film.details.countries) if film.details.countries != None else None}")
        print(f"\tLanguage: {film.details.language}")
        print(f"\tYear: {film.details.year}")

        if "Tel Aviv" in film.dates and len(film.dates["Tel Aviv"]) > 0:
            print("Dates:")
            for cinema_name in film.dates["Tel Aviv"]:
                dates = film.dates["Tel Aviv"][cinema_name]
                if len(dates) == 0:
                    continue

                print(f"\t{cinema_name}:")
                for date in dates:
                    print(f"\t\t{date.ctime()}")

    print("=" * 30)

if __name__ == "__main__":
    main()
