__version__ = "0.1.0"

from .solvers import (
    bisection,
    secant,
    brentq,
    newton,
    halley,
)

from .result import RootResult
from .exceptions import RootFinderError, ConvergenceError