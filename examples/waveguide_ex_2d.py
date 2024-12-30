from photfdtd import Waveguide, Grid, Solve, Index

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide 本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1.0

    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=3e-6, grid_ylength=1, grid_zlength=8e-6,
                grid_spacing=20e-9,
                permittivity=background_index ** 2,
                foldername="basic_ex")

    # set waveguide 设置器件参数
    waveguide = Waveguide(
        xlength=200e-9, ylength=1, zlength=5e-6, refractive_index=index_Re_Si, name="waveguide", grid=grid
    )

    # add waveguide to grid 往 grid 里添加器件
    grid.add_object(waveguide)

    # set a line source with center wl at 1550nm 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="linesource", wavelength=1550e-9, name="source", x=75, y=0, z=60,
                    xlength=400e-9, ylength=0, zlength=0, polarization="x")

    # # set a line detector 设置一个线监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector",
                      x=75,
                      y=0,
                      z=300,
                      xlength=400e-9,
                      ylength=0,
                      zlength=0
                      )

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    # run the FDTD simulation 运行仿真
    grid.run()

    # Save result of simulation 保存仿真结果
    grid.save_simulation()
    # grid.read_simulation(grid.folder)
    grid.source_data()
    grid.detector_profile()
    # Or you can read from a folder 也可以读取仿真结果
    # grid = grid.read_simulation(folder=grid.folder)

    # 如果添加了面监视器，可以绘制监视器范围内电场dB图, as the detector we have added is a linedetector, it's useless
    Grid.dB_map(grid=grid, field="E", field_axis="x")

    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, vmin=-1, vmax=1)

    # 如果添加了监视器，还可以绘制某一点时域场变化曲线，这里选择index=30即监视器中心
    Grid.plot_fieldtime(folder=grid.folder, grid=grid, field_axis="z", index=10, name_det="detector")

    # 绘制频谱
    Grid.visulize_detector(grid=grid, wl_start=1000e-9, wl_end=2000e-9, name_det="detector", index=10, field_axis="x",
                           field="E", folder=None)


