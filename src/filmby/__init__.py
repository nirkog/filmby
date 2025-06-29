from .cinemas.israel.cinema_city import CinemaCityCinema
from .cinemas.israel.lev import LevCinema
from .cinemas.israel.jaffa import JaffaCinema
from .cinemas.israel.rav_hen import RavHenCinema
from .cinemas.israel.canada import CanadaCinema
from .cinemas.israel.cinematheque import CinemathequeCinema
from .cinemas.israel.limbo import LimboCinema
from .cinemas.israel.tlvmuseum import TLVMuseumCinema
from .cinemas.israel.jaffa_hill import JaffaHillCinema
from .cinemas.israel.radical import RadicalCinema

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
