"""
awg is a package for the design and simulation of Arrayed Waveguide Gratings.
"""

__version__ = "1.0.0"

from .AWG import (
    AWG,
    iw,
    aw,
    ow,
    fpr1,
    fpr2,
)

from .Field import Field
from .aperture import Aperture
from .waveguide import Waveguide
from .simulation_options import SimulationOptions
from .simulate import Simulate
from .spectrum import Spectrum
from .spectral_analysis import  Analyse
from .plotfield import plotfield
from .material import *
from .material.material import Material
from .material.dispersion import dispersion
from .distribution import Distribution
from .AWG import AWG
from .awg_simulation import AWG_Simulation

#from .material import (
#    Material,
#    dispersion
#)