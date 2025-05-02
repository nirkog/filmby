import filmby

DAY_NAMES = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]

FILM_NAME_TRANSLATIONS = dict()

def get_day_name(date):
    try:
        return DAY_NAMES[date.weekday()]
    except Exception:
        return ""

def get_film_name_translations():
    if len(FILM_NAME_TRANSLATIONS) == 0:
        for cinema in filmby.CINEMAS["Israel"]:
            FILM_NAME_TRANSLATIONS[cinema.NAME] = cinema.TRANSLATED_NAMES["heb"]

    return FILM_NAME_TRANSLATIONS
