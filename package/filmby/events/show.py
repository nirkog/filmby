from filmby.event import Event, EventDetails

class ShowDetails(EventDetails):
    def __init__(self):
        super().__init__()

class Show(Event):
    TYPE = "במה"

    def __init__(self, name):
        super().__init__(name)

        self.details = ShowDetails()
