from photfdtd import Grid
from photfdtd import fdtd
from photfdtd.fdtd import constants
import matplotlib.pyplot as plt
import numpy as np
import os

if __name__ == "__main__":
    # 读取保存的监视器数据
    filepath = ".\\test_tff_gaussian_old"
    grid = Grid.read_simulation(folder=filepath)
    Grid.plot_field(grid=grid, field="E", field_axis="x")
    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    # grid.calculate_Transmission(field_axis="x", wl_start=400e-9, wl_end=1800e-9)
    source_profile = grid.source_data(time=100e-15)
    # start = 0
    # end = 2141
    source_data = source_profile[:, 25, 0]
    #
    detector_data = np.array(grid._grid.detectors[0].real_E)
    detector_data = detector_data[:, 13, 0]
    wl_start = 400e-9
    wl_end = 1800e-9
    # grid.calculate_Transmission(detector_data=detector_data, source_data=source_data, wl_start=wl_start, wl_end=wl_end)




