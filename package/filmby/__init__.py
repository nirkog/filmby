from filmby.venues.cinemas.israel.cinema_city import CinemaCityCinema
from filmby.venues.cinemas.israel.lev import LevCinema
from filmby.venues.cinemas.israel.jaffa import JaffaCinema
from filmby.venues.cinemas.israel.rav_hen import RavHenCinema
from filmby.venues.cinemas.israel.canada import CanadaCinema
from filmby.venues.cinemas.israel.cinematheque import CinemathequeCinema
from filmby.venues.cinemas.israel.limbo import LimboCinema
from filmby.venues.cinemas.israel.tlvmuseum import TLVMuseumCinema
from filmby.venues.cinemas.israel.jaffa_hill import JaffaHillCinema
from filmby.venues.cinemas.israel.radical import RadicalCinema

CINEMAS = {
    "Israel": [
        CinemathequeCinema,
        # CanadaCinema, # SHUT DOWN :(
        JaffaCinema,
        # CinemaCityCinema,
        LevCinema,
        RavHenCinema,
        LimboCinema,
        TLVMuseumCinema,
        JaffaHillCinema,
        RadicalCinema
    ]
}
