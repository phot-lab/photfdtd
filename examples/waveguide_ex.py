import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":

    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=200, ylength=20, zlength=20, x=100, y=30, z=30, refractive_index=3.47, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=60, grid_zlength=60, grid_spacing=20e-9, total_time=800,
                pml_width_x=10,
                pml_width_y=1,
                pml_width_z=1,
                permittivity=background_index ** 2,
                foldername="test_waveguide")

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置光源
    grid.set_source(source_type="planesource",
                    period=1550e-9/constants.c,
                    name="source",
                    x=100 - waveguide.xlength // 2 + 20,
                    y=30,
                    z=30,
                    xlength=1,
                    ylength=waveguide.ylength + 4,
                    zlength=waveguide.zlength + 4
                    )

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=100 + waveguide.xlength // 2 - 20,
                      y=30,
                      z=30,
                      xlength=1,
                      ylength=waveguide.ylength + 4,
                      zlength=waveguide.zlength + 4
                      )

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve._plot_(axis='z',
                 index=30,
                 filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.save_fig(axis="z",
                  axis_number=30)
    grid.save_fig(axis="x",
                  axis_number=30)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)

