import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
    # 本示例展示了一个基础矩形波导的二维仿真
    # 设置背景折射率
    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=400, ylength=20, zlength=1, x=200, y=75, z=0, refractive_index=3.47, name="waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=150, grid_zlength=1,
                grid_spacing=20e-9,
                total_time=1,
                pml_width_x=40,
                pml_width_y=40,
                pml_width_z=0,
                permittivity=background_index ** 2,
                foldername="basic_ex")

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=80, y=75, z=0,
                    xlength=0, ylength=0, zlength=0)

    # 设置一个线监视器
    # grid.set_detector(detector_type="linedetector",
    #                   name="detector",
    #                   x=300,
    #                   y=75,
    #                   z=0,
    #                   xlength=0 ,
    #                   ylength=60,
    #                   zlength=0
    #                   )

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制z=0截面折射率分布
    solve.plot(axis='z',
               index=0,
               filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制z=0截面场图
    grid.visualize(z=0, showEnergy=True, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)

    # 如果添加了面监视器，可以绘制监视器范围内电场dB图
    # Grid.dB_map(folder=grid.folder, total_time=grid._grid.time_passed, data=data, choose_axis=0,
    #             field="E", name_det="detector", interpolation="spline16", save=True, index="x-y")

    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", axis=2, cross_section="z", axis_number=0, folder=grid.folder)

    # 绘制某一点时域场变化曲线，这里选择index=30即监视器中心
    Grid.plot_fieldtime(folder=grid.folder,data=data,axis=2,index=30, name_det="detector")

    # 绘制频谱
    Grid.compute_frequency_domain(grid=grid, wl_start=1000e-9, wl_end=2000e-9, data=data, name_det="detector",
                             index=30, axis=2, field="E", folder=None)