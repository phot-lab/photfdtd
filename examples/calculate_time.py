import numpy as np
from photfdtd import constants
n = 3.47  # 请输入材料的折射率
L = 900  # "请输入光传输的长度（格数）
grid_spacing = 20  # "请输入空间步长（nm）
c = constants.c  # 单位m/s
dimension = 2

grid_spacing = grid_spacing * 1e-9
L = L * grid_spacing
time_step = 0.99 * grid_spacing / (np.sqrt(dimension) * c)  # 单位：s
t = L * n / c / time_step
print("t = %f" % t)
print("timestep = %f fs" % (time_step * 1e15))
