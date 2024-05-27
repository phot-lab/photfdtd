import numpy as np
import photfdtd.fdtd.constants as constants
n = 1.4555  # 请输入材料的折射率
L = 3777  # "请输入光传输的长度（格数）
grid_spacing = 1000  # "请输入空间步长（nm）
c = constants.c  # 单位m/s
dimension = 3

grid_spacing = grid_spacing * 1e-9
L = L * grid_spacing
time_step = 0.99 * grid_spacing / (np.sqrt(dimension) * c)  # 单位：s
t = L * n / c / time_step
print("%f timesteps, equls %f fs" % (t, t * time_step * 1e15))
print("timestep = %f fs" % (time_step * 1e15))
