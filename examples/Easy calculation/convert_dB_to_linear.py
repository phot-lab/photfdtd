import numpy as np


def linear_to_db(P):
    """
    Convert a linear scale value to decibels (dB).
    :param P: Power in linear scale
    :return: Power in dB
    """
    return - 10 * np.log10(P)


def db_to_linear(dB):
    """
    Convert a dB value to linear scale.
    :param dB: Power in dB
    :return: Power in linear scale
    """
    return 10 ** (-dB / 10)


# Example usage
P_linear = (0.420/0.946) ** 2  # Example power in linear scale
P_db = linear_to_db(P_linear)
print(f"{P_linear} linear scale is {P_db:.2f} dB")

dB_value = 2  # Example power in dB
P_linear_converted = db_to_linear(dB_value)
print(f"{dB_value} dB is {P_linear_converted:.2f} in linear scale")
