""" Python 3D FDTD and FDE simulator, based on the excellent works of
Floris Laporte (https://github.com/flaport/fdtd) and Philip Main (https://github.com/philmain28/philsol?tab=readme-ov-file)"""

__author__ = "Tao Jia", "Li Yang", "Zhenjie Wei", "Chunyu Li"
__version__ = "0.1.1"

from .sbend import Sbend
from .ysplitter import Ysplitter, Taper
from .waveguide import Waveguide
from .arc import Arc
from .directional_coupler import DirectionalCoupler
from .ring import Ring
from .mmi import Mmi
from .grid import Grid
from .solve import Solve
from .analyse import Analyse
from .index import Index
from .mzi import Mzi
from .fiber import Fiber
from .ellipsoid_fiber import Ellipsoid
from .cone import Cone
from .tff import TFF
from .fwg import FWG
from .pc import Hexagonal_PC
from .overlap_calculator import OverlapCalculator
from .intercore_coupling import IntercoreCoupling
from .awg_input import AWG_input
from .awg_output import AWG_output
from .Lantern_3Mode import Lantern_3Mode
from .Lantern_6Mode import Lantern_6Mode
from .hc_arf import HC_ARF
from .plot_awg import Plot_AWG
from .awg_python_main import *

