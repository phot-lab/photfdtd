from photfdtd import Waveguide, Grid, Solve, Index

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide 本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1.4447

    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    # # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=3.5e-6, grid_ylength=1, grid_zlength=6.5e-6, grid_spacing_x=20e-9, grid_spacing_y=20e-9,
                grid_spacing_z=20e-9, permittivity=background_index ** 2, foldername="transmission_ex")

    # set waveguide 设置器件参数
    waveguide = Waveguide(
        xlength=3.5e-6, ylength=1, zlength=0.5e-6, refractive_index=index_Re_Si, name="waveguide", grid=grid
    )

    # add waveguide to grid 往 grid 里添加器件
    grid.add_object(waveguide)

    # set a line source with center wl at 1550nm 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="linesource",
                    wavelength=1000e-9, name="source", y=0, z=1500e-9, pulse_length=10e-15, pulse_type="gaussian",
                    xlength=1500e-9, ylength=0, zlength=0, polarization="x", offset=15e-15)
    #
    # # # set a line detector 设置一个线监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector1",
                      y=0,
                      z=2500e-9,
                      xlength=1500e-9,
                      ylength=0,
                      zlength=0
                      )
    grid.set_detector(detector_type="linedetector",
                      name="detector2",
                      y=0,
                      z=4000e-9,
                      xlength=1500e-9,
                      ylength=0,
                      zlength=0
                      )

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    # # run the FDTD simulation 运行仿真
    # grid.run(time=50e-15)
    #
    # # Save result of simulation 保存仿真结果
    # grid.save_simulation()
    # #
    # # # Or you can read from a folder 也可以读取仿真结果
    grid = grid.read_simulation(folder=grid.folder)
    grid.plot_structure()

    grid.calculate_Transmission(detector_name_1="detector1", detector_name_2="detector2")
