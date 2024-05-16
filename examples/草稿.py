import numpy as np
from photfdtd import constants
delta_neff = 0.4
delta_phi = delta_neff * constants.c * (2 * np.pi) / 1550e-9 * 4e-6
print(delta_phi/(2 * np.pi))
