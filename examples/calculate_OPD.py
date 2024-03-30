import cupy as np

n = 2.79  # 有效折射率
grid_spacing = 50e-9  # 请输入空间步长 (m)
delta_L = 4e-6  # "请输入路程差
lambda0 = 1550e-9  # 输入波长（m)
delta_phi = np.pi / 2
print("光程差为: %f, 相位差为: %f*pi " % (n * delta_L, n * delta_L / lambda0 / (2 * np.pi)))
print("需要的折射率差为: %f " % (delta_phi * (lambda0 / (delta_L * 2 * np.pi))))
print("路程差应为: %f um, 即 %f 个网格 " % (lambda0 * delta_phi / n * 1e6, lambda0 * delta_phi / n / grid_spacing))
