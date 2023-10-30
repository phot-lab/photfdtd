import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=400, ylength=20, zlength=1, x=200, y=100, z=0, refractive_index=3.47, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=200, grid_zlength=1,
                grid_spacing=20e-9,
                total_time=3000,
                pml_width_x=40,
                pml_width_y=40,
                pml_width_z=0,
                permittivity=background_index ** 2,
                foldername="test_waveguide_2D")

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置光源
    grid.set_source(source_type="linesource",
                    period=1550e-9 / constants.c,
                    name="source",
                    x=100,
                    y=100,
                    z=0,
                    xlength=1,
                    ylength=waveguide.ylength + 20,
                    zlength=0
                    )

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
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve.plot(axis='z',
               index=0,
               filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.visualize(z=0, showEnergy=True, show=True, save=True)

    # 可视化监视器数据
    # grid.visualize_detector("detector", "x", "E", show=True, save=True)
    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
    # 绘制监视器范围内光场分布
    try:
        Grid.dB_map(folder="D:/Github_Clone/photfdtd/examples/test_waveguide_2D", total_time=grid._grid.time_passed,
                    data=data, choose_axis=0, field="E", name_det="detector", interpolation="spline16", save=True,
                    index="x-y")
    except:
        pass

    Grid.plot_field(grid=grid, field="E", axis=0, axis_number=0, cross_section="z", folder=grid.folder)
    Grid.plot_field(grid=grid, field="E", axis=1, axis_number=0, cross_section="z", folder=grid.folder)
    Grid.plot_field(grid=grid, field="E", axis=2, axis_number=0, cross_section="z", folder=grid.folder)
