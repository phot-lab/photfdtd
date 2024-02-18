from photfdtd import Arc, Grid, Solve

if __name__ == "__main__":
    background_index = 1.5
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=20, grid_zlength=200, grid_spacing=20e-9,
                foldername="test_arc",
                permittivity=background_index ** 2, )

    # 设置器件参数
    # waveguide1 = Waveguide(
    #     xlength=45, ylength=20, zlength=1, x=80, y=150, z=0, refractive_index=3.47, name="Waveguide1",
    #     grid=grid
    # )
    arc = Arc(outer_radius=60 * 20e-9, ylength=10, width=20, refractive_index=3.47, name="arc",
              angle_phi=0, angle_psi=90,
              grid=grid)
    # waveguide2 = Waveguide(
    #     xlength=20, ylength=40, zlength=1, x=150, y=80, z=0, refractive_index=3.47, name="Waveguide2",
    #     grid=grid
    # )

    # 往 grid 里添加器件
    grid.add_object(arc)
    # grid.add_object(waveguide2)
    # grid.add_object(waveguide1)

    # 设置光源
    # grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source", x=50, y=150, z=0,
    #                 xlength=1, ylength=waveguide1.ylength + 4, zlength=1, polarization="y")

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=150,
    #                   y=30,
    #                   z=11,
    #                   xlength=waveguide2.xlength + 4,
    #                   ylength=1,
    #                   zlength=waveguide1.zlength
    #                   )

    solve = Solve(grid=grid,
                  axis='y',
                  index=10,
                  filepath=grid.folder
                  )

    # We can plot the geometry now 绘制x=0截面结构图
    grid.save_fig(axis="y", axis_number=10)

    # 绘制任一截面
    solve.plot()
    #
    # # 运行仿真
    # grid.run()
    #
    # # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="y", axis="z", axis_index=0, folder=grid.folder)
    #
    # # # 保存仿真结果
    # # grid.save_simulation()
    # #
    # # 读取仿真结果
    # data = grid.read_simulation(folder=grid.folder)
