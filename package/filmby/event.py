import requests
import os
import copy
import datetime

CONTENT_TYPES_TO_FILE_ENDINGS = {
    "image/jpeg": ".jpg"
}

class EventDetails:
    def __init__(self):
        pass

    def get_missing_details(self):
        details = vars(self)
        result = []
        for var in details:
            if details[var] == None:
                result.append(var)

        return result

class Event:
    def __init__(self, name):
        self.name = name
        self.image_url = None
        self.dates = dict()
        self.links = dict()
        self.description = ""
        self.details = None

    def __str__(self):
        return f"{self.name}, {self.links}, {self.dates}"

    def json_serializable(self):
        result = copy.deepcopy(self.__dict__)
        if None != self.details:
            result["details"] = copy.deepcopy(self.details.__dict__)

        for venue in result["dates"]:
            result["dates"][venue] = [str(x) for x in result["dates"][venue]]

        return result
 
    def add_link(self, venue_name, link):
        self.links[venue_name] = link

    def download_image(self, path, file_ending=None):
        if not self.image_url:
            return
        
        # TODO: Add verification everywhere
        response = requests.get(self.image_url)

        if file_ending == None:
            # TODO: This is dumb
            file_ending = CONTENT_TYPES_TO_FILE_ENDINGS[response.headers["Content-Type"]]

        with open("path", os.path.join(path, self.name + file_ending)) as f:
            f.write(response.content)

    def set_image_url(self, url):
        self.image_url = url

    def add_dates(self, venue_name, dates):
        if not venue_name in self.dates:
            self.dates[venue_name] = dates
        else:
            self.dates[venue_name].extend(dates)

        self.dates[venue_name] = list(set(self.dates[venue_name]))
        self.dates[venue_name].sort()

    def get_filtered_dates(self, start_date, end_date=None):
        if None == end_date:
            end_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            end_date += datetime.timedelta(days=1)

        dates = dict()
        for venue in self.dates:
            for d in self.dates[venue]:
                if d >= start_date and d <= end_date:
                    if not venue in dates:
                        dates[venue] = [d]
                    else:
                        dates[venue].append(d)
        return dates
    
    def has_date(self, date):
        for venue in self.dates:
            for d in self.dates[venue]:
                if d.year == date.year and d.month == date.month and d.day == date.day:
                    return True

        return False
