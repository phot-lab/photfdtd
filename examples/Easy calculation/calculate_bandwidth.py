import numpy as np
from photfdtd.fdtd.constants import c
# pulse_oscillation(frequency=, t=, pulselength=, offset=)

# pulselength = 6.49946e-15

# bandwidth = 0.44 / (pulselength)
# print("bandwidth = %f THz" % (bandwidth * 1e-12))
# print("bandwidth = %f um" % (bandwidth * wavelength ** 2 / c * 1e6))


def calculate_pulselength_or_bandwidth(pulselength=None, bandwidth=None, wl_unit: bool = False):
    """
    计算脉宽或带宽。

    :param pulselength: 脉宽，单位为秒 (可选)
    :param bandwidth: 带宽，单位为Hz (可选)
    :return: 如果提供的是脉宽，返回带宽；如果提供的是带宽，返回脉宽。
    :raises ValueError: 如果既未提供脉宽又未提供带宽，或提供了两个参数，则引发异常。
    """
    if pulselength is not None and bandwidth is not None:
        raise ValueError("只能提供一个参数：脉宽或带宽。")

    if pulselength is not None:
        bandwidth = 0.44 / pulselength
        print("bandwidth = %f THz" % (bandwidth * 1e-12))
        print("bandwidth = %f um" % (bandwidth * wavelength ** 2 / c * 1e6))
        return

    if bandwidth is not None:
        if wl_unit:
            # um单位
            bandwidth = bandwidth * c * 1e-12 / 1e6 / wavelength ** 2
        pulselength = 0.44 / bandwidth
        print("pulselength = %f fs" % (pulselength * 1e3))
        return


wavelength = 1550e-9
print("wavelength = %f um" % (wavelength * 1e6))
try:
    calculate_pulselength_or_bandwidth(pulselength=2e-15)  # 输入脉宽 s
    calculate_pulselength_or_bandwidth(bandwidth=(c / 1500e-9 - c / 1600e-9), wl_unit=False)  # 输入带宽为 THz
except ValueError as e:
    print(e)
