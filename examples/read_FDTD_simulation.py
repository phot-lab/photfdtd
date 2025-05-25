from photfdtd import Grid
from photfdtd import fdtd
from photfdtd.fdtd import constants
import matplotlib.pyplot as plt
import numpy as np
import os

if __name__ == "__main__":
    # 读取保存的监视器数据
    filepath = ".\\test_ring_0401_linesource"
    grid = Grid.read_simulation(folder=filepath)
    grid.folder=filepath
    # grid.animate(fps=200)
    # grid.visualize()
    freqs, spectrum1 = grid.visualize_single_detector(name_det='detector_input')
    freqs, spectrum2 = grid.visualize_single_detector(name_det="detector2")
    freqs, spectrum3 = grid.visualize_single_detector(name_det="detector3")


    import matplotlib.pyplot as plt

    plt.plot(freqs, (spectrum2 / spectrum1) ** 2)
    plt.ylabel("Transmission")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_2"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()

    plt.plot(freqs, (spectrum3 / spectrum1) ** 2)
    plt.ylabel("Transmission")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_3"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()


    # 由监视器数据绘制Ex场随时间变化的图像
    # grid.calculate_Transmission(detector_data=detector_data, source_data=source_data, wl_start=wl_start, wl_end=wl_end)




