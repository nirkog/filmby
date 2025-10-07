from filmby.event import Event, EventDetails

class PartyDetails(EventDetails):
    def __init__(self):
        super().__init__()

class Party(Event):
    TYPE = "לילה"

    def __init__(self, name):
        super().__init__(name)

        self.details = PartyDetails()
