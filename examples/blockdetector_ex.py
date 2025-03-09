import utils
from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":
    ### This example is outdated. 需要更新
    # 设置背景折射率
    background_index = 1.0
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=150, grid_zlength=1, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="blockdetector_ex")
    # 设置器件参数
    waveguide = Waveguide(
        grid=grid,
        xlength=400, ylength=20, zlength=1, x=None, y=None, z=0, refractive_index=3.47, name="waveguide",
    )

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置一个点光源，波长为1550nm，波形为连续正弦
    grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=80, y=75, z=0,
                    xlength=0, ylength=0, zlength=0)

    # 设置一个面监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=3e-6,
                      y=None,
                      z=0,
                      xlength=2e-6,
                      ylength=1e-6,
                      zlength=0,
                      axis=None
                      )

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    # run the FDTD simulation 运行仿真
    grid.run()

    # Save the result of simulation, It will be saved in the file that you created when CREATING A GRID Object保存仿真结果，并传给data
    grid.save_simulation()

    # # 读取仿真结果,
    # folder = "D:/Github_Clone/photfdtd/examples/blockdetector_ex"
    # folder = grid.folder
    # data = Grid.read_simulation(folder=folder)

    # 监视器结果可视化
    # 如果添加了面监视器，可以绘制监视器范围内电场dB图, choose_axis参数选择场值的方向0,1,2分别表示"x“,”y“,”z“, field为"E", 或"H",
    # inddex表示绘制的截面
    # Grid.dB_map(grid=grid,field="E", field_axis="x")
    #
    # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", axis=2, folder=folder)
    #
    # # 绘制某一点时域场变化曲线，这里选择index_3d=[50,5,0]即监视器中心
    # Grid.plot_fieldtime(grid=grid, index_3d=[50, 5, 0], name_det="detector")
