from .cinemas.israel.cinema_city import CinemaCityCinema
from .cinemas.israel.lev import LevCinema
from .cinemas.israel.jaffa import JaffaCinema
from .cinemas.israel.rav_hen import RavHenCinema

CINEMAS = {
    "Israel": [
        JaffaCinema,
        CinemaCityCinema,
        LevCinema,
        RavHenCinema
    ]
}
