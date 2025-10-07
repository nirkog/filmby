from filmby.event import Event, EventDetails

class ConcertDetails(EventDetails):
    def __init__(self):
        super().__init__()

        self.doors = None

class Concert(Event):
    TYPE = "הופעות"

    def __init__(self, name):
        super().__init__(name)

        self.details = ConcertDetails()

    def json_serializable(self):
        result = super().json_serializable()
        result["details"]["doors"] = str(result["details"]["doors"])

        return result
