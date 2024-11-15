from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":
    background_index = 1.0

    # 新建一个 grid 对象
    grid = Grid(
        grid_xlength=60, 
        grid_ylength=60, 
        grid_zlength=60,
        grid_spacing=20e-9,
        permittivity=background_index ** 2,
        foldername="test_waveguide"
    )

    # 设置器件参数
    waveguide = Waveguide(
        xlength=20, 
        ylength=20, 
        zlength=45, 
        refractive_index=3.47, 
        name="Waveguide",
        grid=grid
    )

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 绘制任意截面场图
    grid.save_fig(axis="x", axis_number=30)
    grid.save_fig(axis="z", axis_number=200)

    # 设置光源
    grid.set_source(
        source_type="pointsource", 
        wavelength=1550e-9, 
        name="source", 
        z=60,
        xlength=0, 
        ylength=0, 
        zlength=0
    )

    # 设置监视器
    grid.set_detector(
        detector_type="blockdetector",
        name="detector",
        x=240,
        y=30,
        z=20,
        xlength=150,
        ylength=40,
        zlength=0
    )

    # 创建solve对象
    solve = Solve(
        grid=grid,
        axis='z',
        index=100,
        filepath=grid.folder
    )

    # 绘制任一截面折射率分布
    solve.plot()

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
    # 绘制监视器范围内光场分布
    Grid.dB_map(grid=grid, axis="x", field="E", field_axis="x")
