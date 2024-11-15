import numpy as np

def calculate_phase_shift(L, delta_T=20, lam=1550e-9, thermo_coef=1.8e-4):
    """
    Calculate the phase shift given the length of the waveguide.

    :param L: Length of the waveguide (in micrometers)
    :param delta_T: Temperature change (in Kelvin), default is 20K
    :param lam: Wavelength of light (in meters), default is 1550e-9m
    :param thermo_coef: Thermo-optic coefficient (/K), default is 1.8e-4 /K
    :return: Phase shift in multiples of pi
    """
    phase_shift = thermo_coef * delta_T * L * 1e-6 * 2 / lam
    return phase_shift

def calculate_length(phase_shift, delta_T=20, lam=1550e-9, thermo_coef=1.8e-4):
    """
    Calculate the length of the waveguide given the phase shift.

    :param phase_shift: Phase shift in multiples of pi
    :param delta_T: Temperature change (in Kelvin), default is 20K
    :param lam: Wavelength of light (in meters), default is 1550e-9m
    :param thermo_coef: Thermo-optic coefficient (/K), default is 1.8e-4 /K
    :return: Length of the waveguide (in micrometers)
    """
    L = phase_shift * lam / (thermo_coef * delta_T * 2 * np.pi * 1e-6)
    return L

# Example usage
L = 2 * np.pi * 68.525  # um
delta_T = 20  # K
lam = 1550e-9  # m
thermo_coef = 1.8e-4  # /K

# Calculate phase shift given L
phase_shift = calculate_phase_shift(L, delta_T, lam, thermo_coef)
print("相移 = %f pi" % phase_shift)

# Calculate length given phase shift
calculated_L = calculate_length(2 * np.pi, delta_T, lam, thermo_coef)
print("计算出的L = %f um, 对应 % f um 的半径" % (calculated_L, calculated_L / 2 / np.pi))


