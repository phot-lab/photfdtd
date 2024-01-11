from photfdtd import Waveguide, Grid, Solve, Index

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1.0
    index = Index(material="Si", wavelength=1.55)

    # set waveguide设置器件参数
    waveguide = Waveguide(
        xlength=97, ylength=60, zlength=1, x=100, y=100, z=0, refractive_index=3.47, name="waveguide",
        background_index=background_index
    )
    waveguide._rotate_Z(angle=45)

    # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1,
                grid_spacing=20e-9,
                total_time=1,
                pml_width_x=40,
                pml_width_y=40,
                pml_width_z=0,
                permittivity=background_index ** 2,
                foldername="test0109")

    # add waveguide to grid 往 grid 里添加器件
    grid.add_object(waveguide)

    # set a point source 设置一个点光源，波长为1550nm，波形为连续正弦
    # grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=80, y=75, z=0,
    #                 xlength=0, ylength=0, zlength=0)
    #
    # # set a line detector 设置一个线监视器
    # grid.set_detector(detector_type="linedetector",
    #                   name="detector",
    #                   x=300,
    #                   y=75,
    #                   z=0,
    #                   xlength=0,
    #                   ylength=60,
    #                   zlength=0
    #                   )

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
    # data = grid.save_simulation()

    # We can plot the field after simulation绘制z=0截面场图
    grid.save_fig(axis="z",
                  axis_number=0,
                  geo=solve.geometry)
