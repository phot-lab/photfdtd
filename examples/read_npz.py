import numpy as np
import matplotlib.pyplot as plt
from photfdtd import Grid

data = Grid.read_simulation(folder=
                            "D:/下载内容/photfdtd-main/tests/230515 test_sweep/detector_readings_sweep.npz")

detector_bottom_E = data["detector_through (E) 1.550000"]
detector_source_E = data["detector_source (E) 1.550000"]
# grid._plot_sweep_result(folder="D:/下载内容/photfdtd-main/tests/230504 test_sweep")
data = detector_source_E[:, 30, 2]
# data = detector_source_E[:, 30, 2]


# 创建横坐标
x = np.arange(len(data))

# 绘制曲线图
plt.plot(x, data)

# 可选：添加标题、横轴标签和纵轴标签
plt.title('Curve Plot')
plt.xlabel('time (time_step)')
plt.ylabel('E')

# 显示图形
plt.show()

# print(p['detector_source (E) 1.583673'].shape)
