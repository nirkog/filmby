from .cinemas.israel.cinema_city import CinemaCityCinema
from .cinemas.israel.lev import LevCinema
from .cinemas.israel.jaffa import JaffaCinema
from .cinemas.israel.rav_hen import RavHenCinema
from .cinemas.israel.canada import CanadaCinema
from .cinemas.israel.cinematheque import CinemathequeCinema

CINEMAS = {
    "Israel": [
        CinemathequeCinema,
        CanadaCinema,
        JaffaCinema,
        CinemaCityCinema,
        LevCinema,
        RavHenCinema
    ]
}
