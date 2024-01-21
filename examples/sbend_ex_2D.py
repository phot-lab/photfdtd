import utils
from photfdtd import Sbend, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.4447

    # 设置 grid 参数
    grid = Grid(grid_xlength=300 * 20e-9, grid_ylength=200 * 20e-9, grid_zlength=1, grid_spacing=20e-9,
                foldername="test_sbend_2D",
                permittivity=background_index ** 2,
                )

    # 设置波导参数
    sbend = Sbend(
        xlength=200 * 20e-9, ylength=100 * 20e-9, zlength=1, direction=-1, width=20, refractive_index=3.47,
        name="sbend",
        grid=grid
    )

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source", x=1e-6, y=2.8e-6, z=0,
                    xlength=1 * 20e-9, ylength=20 * 20e-9, zlength=1, polarization="y")

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
    grid.save_fig(axis="z", axis_number=0)
    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制截面
    solve.plot()

    # 运行仿真
    grid.run()


    Grid.plot_field(grid=grid, field="E", field_axis="y", axis="z", axis_index=0, folder=grid.folder)
    grid.save_fig(axis="z", axis_number=0, show_energy=True)

