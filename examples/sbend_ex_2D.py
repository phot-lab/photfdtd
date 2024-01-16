from photfdtd import Sbend, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    # 设置 grid 参数
    grid = Grid(grid_xlength=200 * 20e-9, grid_ylength=150 * 20e-9, grid_zlength=1, grid_spacing=20e-9,
                total_time=600,
                pml_width_x=20,
                pml_width_y=10,
                pml_width_z=0,
                foldername="test_sbend",
                permittivity=background_index ** 2,
                )

    # 设置波导参数
    sbend = Sbend(
        xlength=200 * 20e-9, ylength=100 * 20e-9, zlength=1, direction=-1, width=20, refractive_index=3.47,
        name="sbend",
        grid=grid
    )

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source", x=30, y=110, z=0,
                    xlength=1 * 20e-9, ylength=20 * 20e-9, zlength=1)

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=175,
    #                   y=40,
    #                   z=13,
    #                   xlength=1,
    #                   ylength=20,
    #                   zlength=20
    #                   )

    # 添加器件
    grid.add_object(sbend)

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制截面
    solve.plot()

    # 运行仿真
    grid.run()

    grid.save_fig(axis="z",
                  axis_number=0)
