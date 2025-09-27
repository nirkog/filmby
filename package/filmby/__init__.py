from filmby.venues.cinemas.cinema_city import CinemaCityCinema
from filmby.venues.cinemas.lev import LevCinema
from filmby.venues.cinemas.jaffa import JaffaCinema
from filmby.venues.cinemas.rav_hen import RavHenCinema
from filmby.venues.cinemas.canada import CanadaCinema
from filmby.venues.cinemas.cinematheque import CinemathequeCinema
from filmby.venues.cinemas.limbo import LimboCinema
from filmby.venues.cinemas.tlvmuseum import TLVMuseumCinema
from filmby.venues.cinemas.jaffa_hill import JaffaHillCinema
from filmby.venues.cinemas.radical import RadicalCinema

CINEMAS = [
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
