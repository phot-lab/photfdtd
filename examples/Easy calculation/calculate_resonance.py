import numpy as np
import photfdtd.fdtd.constants as constants

n = 3.5  # 请输入材料的折射率
L = 5e-6 * 2 * np.pi + 2 * 4e-6  # m
f = 20  # Hz
c = constants.c  # 单位m/s
dimension = 2
muf = c / n / 2 / L


def find_closest_wavelengths(muf, x, num_results=5):
    c = 299792458  # 光速 (m/s)

    # 计算最接近 x 的 k
    k_center = round(c / (x * muf))

    # 生成附近的整数倍 k
    k_values = np.arange(k_center - num_results // 2, k_center + num_results // 2 + 1)

    # 计算对应的波长
    wavelengths = c / (k_values * muf)

    # 按照与 x 的接近程度排序
    wavelengths = sorted(wavelengths, key=lambda xi: abs(xi - x))

    return wavelengths


x = 1550e-9  # 目标波长 (m)

closest_wavelengths = find_closest_wavelengths(muf, x)
print(f"resonance frequencies are the multiples of {muf} Hz")
print(f"resonance wavelengths that are closest to {x} are: {closest_wavelengths}")
