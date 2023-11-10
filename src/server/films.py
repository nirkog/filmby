import time
import threading
import pickle
import os
from datetime import date, timedelta

import filmby

films = []

class IntervalThread(threading.Thread):
    def __init__(self, interval, func, args=(), kwargs=dict()):
        super(IntervalThread, self).__init__()
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        global started
        while True:
            # TODO: Maybe take interval from end to start
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)

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

def start_film_updating_thread(interval):
    global films

    if os.path.exists("cache/films.bin"):
        with open("cache/films.bin", "rb") as f:
            films = pickle.load(f)

    print(len(films))

    thread = IntervalThread(interval, update_films)
    thread.start()

TMP_DESC = """
"חיים שלמים", שהוכתר כבר על ידי המבקרים כ"סרט הגדול הראשון של השנה", הוא דרמה יפהפייה, חכמה ונוגעת ללב, שהוקרנה בפסטיבל ברלין ורבים כבר חוזים שתיקח חלק משמעותי בעונת הפרסים הבאה ובטקס האוסקר. סרט הביכורים של סלין סונג הוא יצירה קולנועית מהפנטת ומדויקת, שנשארת עם הצופה הרבה אחרי היציאה מהאולם.

נורה והא-סונג, שני חברי ילדות בעלי קשר ייחודי כפי שיש רק לילדים, נאלצים להיפרד כשמשפחתה של נורה עוזבת את סיאול ומהגרת לקנדה. שני עשורים לאחר מכן, הם נפגשים שוב בניו יורק. הפגישה המחודשת מעלה שאלות על גורל, אהבה, והבחירות שמעצבות את החיים שלנו.
"""

def update_films(interval=None):
    global films

    print("Updating films")

    country = "Israel"
    town = "Tel Aviv"
    cinemas = []

    for cinema in filmby.CINEMAS[country]:
        if town in cinema.TOWNS:
            cinemas.append(cinema())

    new_films = []
    for cinema in cinemas:
        for i in range(0, 7):
            cinema_films = cinema.get_films_by_date(date.today() + timedelta(i), town)
            if cinema_films != None:
                new_films.extend(cinema_films)

    merge_films(new_films)

    for film in new_films:
        film.description = TMP_DESC

    films = new_films

    if not os.path.exists("cache/"):
        os.mkdir("cache")

    with open("cache/films.bin", "wb") as f:
        pickle.dump(films, f)

    print(f"Finished updating with {len(films)} films")

    # for film in films:
    #     if len(film.links) > 2:
    #         print(film.name)
    #         print(film.links)
    #         print(film.image_url)
    #         print(film.dates)
