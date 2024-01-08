from photfdtd import Waveguide, Grid, Solve, Index

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1.0
    index = Index(material="Si", wavelength=1.55)

    # set waveguide设置器件参数
    waveguide = Waveguide(
        xlength=400, ylength=20, zlength=1, x=200, y=75, z=0, refractive_index=3.47, name="waveguide",
        background_index=background_index
    )

    # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=150, grid_zlength=1,
                grid_spacing=20e-9,
                total_time=1,
                pml_width_x=40,
                pml_width_y=40,
                pml_width_z=0,
                permittivity=background_index ** 2,
                foldername="basic_ex")

    # add waveguide to grid 往 grid 里添加器件
    grid.add_object(waveguide)

    # set a point source 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=80, y=75, z=0,
                    xlength=0, ylength=0, zlength=0)

    # set a line detector 设置一个线监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector",
                      x=300,
                      y=75,
                      z=0,
                      xlength=0,
                      ylength=60,
                      zlength=0
                      )

    # create a Solve object. You can use it to solve the eigenmodes (see eigenmode_solver_ex) 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )

    # plot the refractive index map on z=0绘制z=0截面折射率分布
    solve.plot()

    # run the FDTD simulation 运行仿真
    grid.run()

    # Save the result of simulation, It will be saved in the file that you created when CREATING A GRID Object保存仿真结果，并传给data
    data = grid.save_simulation()

    # We can plot the field after simulation绘制z=0截面场图
    grid.save_fig(axis="z",
                  axis_number=0,
                  geo=solve.geometry)

    # 也可以读取仿真结果
    # data = grid.read_simulation(folder=grid.folder)

    # 如果添加了面监视器，可以绘制监视器范围内电场dB图, as the detector we have added is a linedetector, it's useless
    # Grid.dB_map(folder=grid.folder, total_time=grid._grid.time_passed, data=data, choose_axis=0,
    #             field="E", name_det="detector", interpolation="spline16", save=True, index="x-y")

    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis=2, axis="z", axis_index=0, folder=grid.folder)

    # 如果添加了监视器，还可以绘制某一点时域场变化曲线，这里选择index=30即监视器中心
    Grid.plot_fieldtime(folder=grid.folder, data=data, field_axis=2, index=30, name_det="detector")

    # 绘制频谱
    Grid.compute_frequency_domain(grid=grid, wl_start=1000e-9, wl_end=2000e-9, data=data, name_det="detector",
                                  index=30, axis=2, field="E", folder=None)
