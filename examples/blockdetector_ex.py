import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
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
                total_time=600,
                pml_width_x=40,
                pml_width_y=40,
                pml_width_z=0,
                permittivity=background_index ** 2,
                foldername="blockdetector_ex")

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=80, y=75, z=0,
                    xlength=0, ylength=0, zlength=0)

    # 设置一个面监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=120,
                      y=75,
                      z=0,
                      xlength=80,
                      ylength=10,
                      zlength=0
                      )

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

    # 绘制z=0截面场图
    grid.visualize(z=0, showEnergy=True, show=True, save=True)

    # # 读取仿真结果,
    # folder = "D:/Github_Clone/photfdtd/examples/blockdetector_ex"
    folder = grid.folder
    data = Grid.read_simulation(folder=folder)

    # 监视器结果可视化
    # 如果添加了面监视器，可以绘制监视器范围内电场dB图, choose_axis参数选择场值的方向0,1,2分别表示"x“,”y“,”z“, field为"E", 或"H",
    # inddex表示绘制的截面
    Grid.dB_map(folder=folder, total_time=800, data=data, axis="x-y", field_axis=2, field="E", name_det="detector",
                interpolation="spline16", save=True)

    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis=2, axis="z", axis_index=0, folder=folder)

    # 绘制某一点时域场变化曲线，这里选择index_3d=[50,5,0]即监视器中心
    Grid.plot_fieldtime(folder=folder, data=data, field_axis=2, index_3d=[50, 5, 0], name_det="detector")