from photfdtd import Waveguide, Grid, Solve, constants, Analyse
import matplotlib.pyplot as plt
import os
import numpy as np

if __name__ == "__main__":
    folder = "D://Github_Clone//photfdtd//test//test_sbend_1009"
    data = Grid.read_simulation(folder=folder)

    analyse_source = Analyse(E=data["detector_source (E)"], H=data["detector_source (H)"], grid_spacing=20e-9)
    # analyse_source.plot()
    analyse_through = Analyse(E=data["detector_through (E)"], H=data["detector_through (H)"], grid_spacing=20e-9)
    b = np.sum(analyse_through.Power["power_positive_x"])
    a = np.sum(analyse_source.Power["power_positive_x"])
    T = b/a
    # print("T = %f" % b/a)


    # 创建一个图像和轴
    fig, ax = plt.subplots()

    # axis = 1
    # 设置X轴和Y轴标签
    ax.set_xlabel('timestep')
    
    E_data = data["detector_through (E)"]
    for axis in range(3):
        plt.plot(range(len(E_data)), E_data[:, 0, axis], linestyle='-', label="Experiment")
        if axis == 1:
            ax.set_ylabel('Ey')
            plt.title("photfdtd_E%s-t" % "y")
            file_name = "Ey"
        elif axis == 0:
            ax.set_ylabel('Ex')
            plt.title("photfdtd_E%s-t" % "x")
            file_name = "Ex"
        elif axis == 2:
            ax.set_ylabel('Ez')
            plt.title("photfdtd_E%s-t" % "z")
            file_name = "Ez"
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.clf()
        plt.close()
