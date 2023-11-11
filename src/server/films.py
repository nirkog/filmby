import time
import threading
import pickle
import os
from datetime import date, timedelta

import filmby

MAX_THREAD_COUNT = 100

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

def same_film_heuristic(first, second):
    if first.have_same_name(second):
        return True
    
    return False

def merge_films(films):
    i = 0
    found_names = dict()
    print("AS")
    while i < len(films):
        film = films[i]

        found = False
        for j in range(0, i):
            other = films[j]
            if same_film_heuristic(film, other):
                found = True
                other.merge(film)
                films.remove(film)
                break

        if found:
            continue

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

def get_films_by_date(cinema, date, town, arr, condition):
    result = cinema.get_films_by_date(date, town)
    if result != None:
        arr.extend(result)
    with condition:
        condition.notify_all()

def update_films(interval=None):
    global films

    start = time.time()

    print("Updating films")

    country = "Israel"
    town = "Tel Aviv"
    cinemas = []

    for cinema in filmby.CINEMAS[country]:
        if town in cinema.TOWNS:
            cinemas.append(cinema())

    threads = []
    new_films = []
    condition = threading.Condition()
    for cinema in cinemas:
        for i in range(0, 7):
            if threading.active_count() > MAX_THREAD_COUNT:
                with condition:
                    condition.wait()
            threads.append(threading.Thread(target=get_films_by_date, args=(cinema, date.today() + timedelta(i), town, new_films, condition,)))
            threads[-1].start()

    for thread in threads:
        thread.join()

    merge_films(new_films)

    for film in new_films:
        film.description = TMP_DESC

    films = new_films

    if not os.path.exists("cache/"):
        os.mkdir("cache")

    with open("cache/films.bin", "wb") as f:
        pickle.dump(films, f)

    print(f"Finished updating with {len(films)} films, took {time.time() - start}s")
