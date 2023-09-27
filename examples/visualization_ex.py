import time

from photfdtd import Waveguide, Arc, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    waveguide0 = Waveguide(
        xlength=50, ylength=50, zlength=50, x=50, y=50, z=50, refractive_index=3.47, name="Waveguide0",
        background_index=background_index
    )
    # 设置器件参数
    # waveguideX = Waveguide(
    #     xlength=50, ylength=10, zlength=10, x=50, y=20, z=20, refractive_index=3.47, name="Waveguide1",
    #     background_index=background_index
    # )

    # waveguideY = Waveguide(
    #     xlength=10, ylength=50, zlength=10, x=20, y=60, z=20, refractive_index=3.47, name="Waveguide2",
    #     background_index=background_index
    # )
    #
    # waveguideZ = Waveguide(
    #     xlength=10, ylength=10, zlength=50, x=20, y=20, z=40, refractive_index=3.47, name="Waveguide3",
    #     background_index=background_index
    # )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=100, grid_ylength=100, grid_zlength=100, grid_spacing=20e-9, total_time=10,
                foldername="test_visualization",
                pml_width_x=15,
                pml_width_y=10,
                pml_width_z=5,
                permittivity=background_index ** 2, )

    # 往 grid 里添加器件
    grid.add_object(waveguide0)
    # grid.add_object(waveguideX)
    # grid.add_object(waveguideY)
    # grid.add_object(waveguideZ)

    # 设置光源
    grid.set_source(source_type="planesource",
                    period=1550e-9 / constants.c,
                    name="source",
                    x=20,
                    y=50,
                    z=40,
                    xlength=1,
                    ylength=waveguide0.ylength + 12,
                    zlength=waveguide0.zlength + 12
                    )

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=50,
                      y=50,
                      z=50,
                      xlength=waveguide0.xlength + 8,
                      ylength=waveguide0.ylength + 8,
                      zlength=waveguide0.xlength + 8
                      )
    print(grid)
    solve = Solve(grid=grid)

    # 绘制任一截面
    # solve._plot_(axis='z',
    #              index=11,
    #              filepath=grid.folder)
    # solve._plot_(axis='x',
    #              index=100,
    #              filepath=grid.folder)

    # 运行仿真
    # grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    # grid.save_fig(axis="y",
    #               axis_number=50)
    # grid.save_fig(axis="z",
    #               axis_number=50)
    # grid.save_fig(axis="x",
    #               axis_number=50)
    stime = time.time()
    grid.visualize(x=50, showEnergy=True, show=True, save=True)
    sstime_1 = time.time()
    grid.visualize(y=50, showEnergy=True, show=True, save=True)
    sstime_2 = time.time()
    grid.visualize(z=50, showEnergy=True, show=True, save=True)
    sstime_3 = time.time()
    print(sstime_1-stime)
    print(sstime_2 - sstime_1)
    print(sstime_3 - sstime_2)

    # grid.visualize(x=50, showEnergy=False, show=True, save=True)
    # grid.visualize(y=50, showEnergy=False, show=True, save=True)
    # grid.visualize(z=50, showEnergy=False, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
