import utils
from photfdtd import Waveguide, Grid, Solve, constants


if __name__ == "__main__":

    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=340, ylength=20, zlength=1, x=170, y=30, z=0, refractive_index=3.47, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=340, grid_ylength=60, grid_zlength=1, grid_spacing=20e-9, total_time=1800,
                pml_width_x=80,
                pml_width_y=1,
                pml_width_z=0,
                permittivity=background_index ** 2,
                foldername="test_animate")
    # time_step = 4.67013e-17
    # 往 grid 里添加器件
    # grid.add_object(waveguide)
    #
    # # 设置光源
    # grid.set_source(source_type="linesource",
    #                 period=1550e-9/constants.c,
    #                 name="source",
    #                 x=85,
    #                 y=30,
    #                 z=0,
    #                 pulse_type="gaussian",
    #                 waveform=False,
    #                 xlength=0,
    #                 ylength=waveguide.ylength,
    #                 zlength=0,
    #                 pulse_length=10.2381e-15,
    #                 offset=15.0284e-15
    #                 )
    #
    # # 设置监视器
    # grid.set_detector(detector_type="linedetector",
    #                   name="detector",
    #                   x=170,
    #                   y=30,
    #                   z=0,
    #                   xlength=0,
    #                   ylength=waveguide.ylength + 10,
    #                   zlength=0
    #                   )
    #
    # # grid.set_detector(detector_type="linedetector",
    # #                   name="detector_source",
    # #                   x=100 - waveguide.xlength // 2 + 20,
    # #                   y=30,
    # #                   z=0,
    # #                   xlength=0,
    # #                   ylength=waveguide.ylength + 10,
    # #                   zlength=0
    # #                   )
    #
    # # 创建solve对象
    # solve = Solve(grid=grid)
    #
    # # 绘制任一截面折射率分布
    # solve._plot_(axis='z',
    #              index=0,
    #              filepath=grid.folder)
    #
    # # 运行仿真
    # grid.run(animate=True,
    #          step=20,
    #          axis_number=0,
    #          axis="z")

    # 保存仿真结果
    grid.save_simulation()
    grid.animate()

    # 绘制任意截面场图
    # grid.save_fig(axis="z", axis_number=0, animate=d)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
    print(data)
