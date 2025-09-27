from abc import ABC, abstractmethod

class Venue(ABC):
    TRANSLATED_NAMES = None
    NAME = None

    def __init__(self):
        self.details_cache = dict()

    def _add_to_details_cache(self, event, details):
        self.details_cache[event.links[self.NAME]] = details

    def _get_details_from_cache(self, event):
        if self.NAME in event.links:
            if event.links[self.NAME] in self.details_cache:
                return self.details_cache[event.links[self.NAME]] 
        return None

    @abstractmethod
    def get_events_by_date(self, date):
        pass
    
    @abstractmethod
    def get_event_details(self, event):
        pass
    
    @abstractmethod
    def get_provided_event_details(self):
        pass

    def clean_cache(self):
        self.details_cache = dict()
