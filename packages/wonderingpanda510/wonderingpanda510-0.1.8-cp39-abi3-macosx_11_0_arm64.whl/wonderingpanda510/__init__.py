from wonderingpanda510._core import hello_from_bin
from . import differential, matrix, distributions	
from .matrix import rowswap, rowscale, rowreplacement, rref
from .distributions import exponentialdist, poissiondist

__all__ = ["hello", "differential", "matrix", "distributions",
           "rowswap", "rowscale", "rowreplacement", "rref", "poissiondist", "exponentialdist"]

def hello() -> str:
    return hello_from_bin()
