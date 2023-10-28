from datetime import date, timedelta

import filmby

def merge_films(films):
    i = 0
    found_names = dict()
    while i < len(films):
        film = films[i]

        found_film = None
        for name in found_names:
            if film.have_same_name(films[found_names[name]]):
                found_film = films[found_names[name]]

        if found_film != None:
            found_film.merge(film)
            films.remove(film)
        else:
            found_names[film.name] = i
            i += 1

def main():
    town = "Tel Aviv"
    cinemas = []

    for cinema in filmby.CINEMAS:
        if town in cinema.TOWNS:
            cinemas.append(cinema(town))

    films = []
    for cinema in cinemas:
        cinema_films = cinema.get_films_by_date(date.today() + timedelta(2))
        if cinema_films != None:
            films.extend(cinema_films)

    merge_films(films)

    for film in films:
        print(film.name)
        
    print(len(films))
    # print(films[0].name)
    # print(films[0].image_url)
    # print(films[0].dates)
    # print(films[0].links)

if __name__ == "__main__":
    main()
