import photfdtd.fdtd
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
photfdtd.fdtd.set_backend("torch") # 设置使用 torch 后端
from photfdtd import Waveguide, Grid, Solve, Index

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide 本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1

    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    # # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=4e-6, grid_ylength=1, grid_zlength=4e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_torch")

    # set waveguide 设置器件参数
    waveguide = Waveguide(
        xlength=400e-9, ylength=1, zlength=4e-6, refractive_index=index_Re_Si, name="waveguide", grid=grid
    )

    # add waveguide to grid 往 grid 里添加器件
    grid.add_object(waveguide)
    # grid.del_object(waveguide)
    # set a line source with center wl at 1550nm 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="linesource",
                    wavelength=1550e-9, name="source", x=1500e-9, y=0, z=1200e-9, pulse_length=30e-15,
                    xlength=400e-9, ylength=0, zlength=0, polarization="x", pulse_type="gaussian")
    #
    # # # set a line detector 设置一个线监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector1",
                      x=1500e-9,
                      y=0,
                      z=1500e-9,
                      xlength=400e-9,
                      ylength=0,
                      zlength=0
                      )
    # grid.set_detector(detector_type="linedetector",
    #                   name="detector2",
    #                   x=1500e-9,
    #                   y=0,
    #                   z=7000e-9,
    #                   xlength=400e-9,
    #                   ylength=0,
    #                   zlength=0
    #                   )
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector3",
    #                   axis="y",
    #                   xlength=1e-6,
    #                   ylength=0,
    #                   zlength=2e-6,
    #                   )

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    # run the FDTD simulation 运行仿真
    grid.run(animate=False, save=True, interval=20)

    # # Or you can read from a folder 也可以读取仿真结果
    # grid._grid.time_steps_passed = 3000
    # grid = grid.read_simulation(folder=grid.folder)
    grid.visualize()

    grid.calculate_Transmission(detector_name_1="detector1", detector_name_2="detector2")
    grid.plot_n()
    grid.plot_field(grid=grid, field="E", field_axis="x", axis="y")
    grid.plot_field(grid=grid, field="E", field_axis="y", axis="y")
    grid.plot_field(grid=grid, field="E", field_axis="z", axis="y")
    grid.plot_field(grid=grid, field="H", field_axis="x", axis="y")
    grid.plot_field(grid=grid, field="H", field_axis="y", axis="y")
    grid.plot_field(grid=grid, field="H", field_axis="z", axis="y")

    # 如果添加了面监视器，可以绘制监视器范围内电场dB图, as the detector we have added is a linedetector, it's useless
    # Grid.dB_map(grid=grid, field="E", field_axis="x")
    #
    # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, vmin=-1, vmax=1)
    #
    # # 如果添加了监视器，还可以绘制某一点时域场变化曲线，这里选择index=30即监视器中心
    # Grid.plot_fieldtime(folder=grid.folder, grid=grid, field_axis="z", index=10, name_det="detector")
    #
    # # 绘制频谱
    # Grid.compute_frequency_domain(grid=grid, wl_start=1000e-9, wl_end=2000e-9, name_det="detector",
    #                               index=10, field_axis="x", field="E", folder=None)
