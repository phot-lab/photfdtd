import utils
from photfdtd import Ysplitter, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    # 设置 grid 参数
    grid = Grid(grid_xlength=250, grid_ylength=1, grid_zlength=300, grid_spacing=20e-9,
                foldername="test_ysplitter_2D", permittivity=background_index ** 2)

    # 设置器件参数
    ysplitter = Ysplitter(xlength=200, ylength=1, zlength=250, direction=1, width=20,
                          name="ysplitter",
                          refractive_index=3.47, zlength_waveguide=80, xlength_taper=40, zlength_taper=40,
                          width_sbend=20, grid=grid)

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source", x=2.5e-6, y=0, z=1e-6,
                    xlength=30, ylength=1, zlength=1, polarization="x")

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=175,
    #                   y=63,
    #                   z=13,
    #                   xlength=1,
    #                   ylength=25,
    #                   zlength=22
    #                   )

    grid.add_object(ysplitter)

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='y',
                  index=0,
                  filepath=grid.folder)

    # 绘制任一截面折射率分布
    solve.plot()

    # 运行仿真
    grid.run()

    grid.save_fig(axis="y", axis_number=0)
    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder, vmax=4)
