import utils
from photfdtd import Waveguide, Grid, Solve, constants
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

if __name__ == "__main__":

    data = Grid.read_simulation(folder="D://Github_Clone//photfdtd//examples//test_plane_wave_0904")
    data = data["detector (E)"]
    # 创建一个图像和轴
    fig, ax = plt.subplots()

    start_frame = 0
    end_frame = -1
    # 初始化显示第一个时间步的数据
    line, = ax.plot(data[start_frame][:, 0], data[start_frame][:, 2], 'b-')  # 绘制第二维和第三维的数据

    # 设置X轴和Y轴范围
    ax.set_xlim(0, 30)  # 适应坐标点范围
    ax.set_ylim(-3, 3)  # 适应电场数据范围

    title = ax.text(0.5, 1.05, '', transform=ax.transAxes, ha='center')
    # 设置X轴和Y轴标签
    ax.set_xlabel('xlength')
    ax.set_ylabel('Ez')


    # 定义一个函数，用于更新图像内容
    def update(frame):
        if start_frame <= frame <= end_frame:
            line.set_xdata(np.arange(30))  # 更新X轴数据
            line.set_ydata(data[frame][:, 2])  # 更新Y轴数据
            title.set_text(f'Time Step: {frame}')


    # 创建动画
    ani = FuncAnimation(fig, update, frames=len(data), repeat=False, interval=4000 / len(data))
    ani.save('simple_animation.mp4', writer='ffmpeg', fps=100)
    plt.show()

