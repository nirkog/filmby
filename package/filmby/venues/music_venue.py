from abc import ABC, abstractmethod

from filmby.venue import Venue

class MusicVenue(Venue):
    VENUE_TYPE_NAMES = {
        "en": "Music venues",
        "he": "הופעות",
    }

    def __init__(self):
        super().__init__()
