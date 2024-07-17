import numpy as np


def calculate_L(y, lambda_0, delta_n):
    """
    Calculate L given y, lambda_0, and delta_n.
    :param y: P2 / P0
    :param lambda_0: Wavelength
    :param delta_n: Refractive index difference
    :return: L
    """
    L = (lambda_0 / (np.pi * delta_n)) * np.arcsin(np.sqrt(y))
    return L


def calculate_y(L, lambda_0, delta_n):
    """
    Calculate y given L, lambda_0, and delta_n.
    :param L: Length
    :param lambda_0: Wavelength
    :param delta_n: Refractive index difference
    :return: y (P2 / P0)
    """
    y = (np.sin((L * np.pi * delta_n) / lambda_0)) ** 2
    return y


# Example usage
lambda_0 = 1.55e-6  # Example wavelength in meters
n2 = 2
n1 = 1
delta_n = n2 - n1  # Example refractive index difference

# Given y, calculate L
y = 0.5
L = calculate_L(y, lambda_0, delta_n)
print(f"For y = {y}, L = {L * 1e6} um")

# Given L, calculate y
L_given_in_um = 0.1  # Example length in meters
y_calculated = calculate_y(L_given_in_um * 1e-6, lambda_0, delta_n)
print(f"For L = {L_given_in_um * 1e6} um, y = {y_calculated:.6f}")
