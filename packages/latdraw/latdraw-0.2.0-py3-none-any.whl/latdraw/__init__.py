"""Top-level package for latdraw."""

__author__ = """Stuart Derek Walker"""
__email__ = "stuart.walker@desy.de"
__version__ = "0.0.0"


import warnings

from latdraw.interfaces import read, read_bdsim_survey, read_mad8, read_madx
from latdraw.latdraw import draw, draw_survey
from latdraw.plot import (
    plot_optics,
    subplots_with_lattice,
    subplots_with_lattices,
    two_axes_figure,
)

from . import optics

# from latdraw.lattice import Beamline


try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import ocelot
    from latdraw.interfaces import lattice_from_ocelot
except ImportError:
    pass
