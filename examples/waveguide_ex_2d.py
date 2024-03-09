import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=200, grid_zlength=1,
                grid_spacing=20e-9,
                permittivity=background_index ** 2,
                foldername="test_waveguide_2D")
    # 设置器件参数
    waveguide = Waveguide(
        xlength=400, ylength=20, zlength=1, x=200, y=100, z=0, refractive_index=3.47, name="Waveguide", grid=grid
    )

    # 往 grid 里添加器件
    grid.add_object(waveguide)
    grid.save_fig(axis="z", axis_number=0)

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source", x=100, y=100, z=0, xlength=1,
                    ylength=waveguide.ylength + 20, zlength=0, polarization="x")

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=240,
    #                   y=100,
    #                   z=0,
    #                   xlength=150,
    #                   ylength=40,
    #                   zlength=0)

    # 创建solve对象
    solve = Solve(grid=grid, axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制任一截面折射率分布
    solve.plot()

    # 运行仿真
    grid.run()



    # 保存仿真结果，并传给data
    data = grid.save_simulation()

    # 也可以读取仿真结果
    # data = grid.read_simulation(folder=grid.folder)
    # 如果设置了监视器，绘制监视器范围内光场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="z", axis_index=0, folder=grid.folder,
                    vmax=1)


