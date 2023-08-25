import numpy as np
n = 2.79 # 请输入材料的折射率
grid_spacing = 50e-9 # 请输入空间步长 (m)
delta_L = 50 * grid_spacing # "请输入路程差 (空间步长)
lambda0 = 1550e-9 # 输入波长（m)

print("光程差为: %f, 相位差为: %f*pi " % (n*delta_L, n*delta_L / lambda0 / np.pi))

delta_theta = np.pi
print("路程差应为: %f m, 即 %f 个网格 " %(lambda0 * delta_theta / n, lambda0 * delta_theta / n /grid_spacing))
