import time

from photfdtd import Waveguide, Arc, Grid, Solve
import photfdtd.fdtd.constants as constants

if __name__ == "__main__":
    background_index = 1.0

    waveguide0 = Waveguide(
        xlength=20, ylength=20, zlength=20, x=25, y=25, z=25, refractive_index=3.47, name="Waveguide0",
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
    grid = Grid(grid_xlength=50, grid_ylength=50, grid_zlength=50, grid_spacing=20e-9, total_time=300,
                foldername="test_visualization",
                pml_width_x=5,
                pml_width_y=5,
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
                    x=10,
                    y=25,
                    z=25,
                    xlength=1,
                    ylength=waveguide0.ylength + 4,
                    zlength=waveguide0.zlength + 4
                    )

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=25,
                      y=25,
                      z=25,
                      xlength=waveguide0.xlength + 2,
                      ylength=waveguide0.ylength + 2,
                      zlength=waveguide0.zlength + 2
                      )
    grid.set_detector(detector_type="linedetector",
                      name="detector1",
                      x=25,
                      y=25,
                      z=25,
                      xlength=waveguide0.xlength,
                      ylength=0,
                      zlength=0
                      )
    solve = Solve(grid=grid)

    # 绘制任一截面
    # solve._plot_(axis='z',
    #              index=11,
    #              filepath=grid.folder)
    # solve._plot_(axis='x',
    #              index=100,
    #              filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    # grid.save_fig(axis="y",
    #               axis_number=50)
    # grid.save_fig(axis="z",
    #               axis_number=50)
    # grid.save_fig(axis="x",
    #               axis_number=50)
    stime = [time.time()]
    grid.visualize(x=25, showEnergy=True, show=True, save=True)
    stime.append(time.time())
    grid.visualize(y=25, showEnergy=True, show=True, save=True)
    stime.append(time.time())
    grid.visualize(z=25, showEnergy=True, show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector", "x", "E", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector", "y", "E", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector", "z", "E", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector", "x", "H", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector", "y", "H", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector", "z", "H", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector1", "x", "E", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector1", "y", "E", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector1", "z", "E", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector1", "x", "H", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector1", "y", "H", show=True, save=True)
    stime.append(time.time())
    grid.visualize_detector("detector1", "z", "H", show=True, save=True)
    stime.append(time.time())
    for index in range(1, len(stime)):
        print(stime[index] - stime[index-1])

    # grid.visualize(x=50, showEnergy=False, show=True, save=True)
    # grid.visualize(y=50, showEnergy=False, show=True, save=True)
    # grid.visualize(z=50, showEnergy=False, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
