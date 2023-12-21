from photfdtd import TFF, Grid, Solve

if __name__ == "__main__":
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.0

    # 制作一个11层厚，1550nm波长的增返膜
    tff = TFF(
        xlength=200,
        ylength=220,
        zlength=1,
        x=100,
        y=0,
        z=0,
        name="TFF",
        layers=10,
        axis="y",
        low_index=1.35,
        high_index=2.35,
        dh=8,
        dl=14,
        background_index=background_index
    )

    grid = Grid(grid_xlength=200, grid_ylength=300, grid_zlength=1, grid_spacing=grid_spacing, total_time=700,
                foldername="test_fft",
                permittivity=background_index ** 2)

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, name="source", x=100, y=275, z=1, xlength=50,
                    ylength=1, zlength=0)
    #
    # # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector1",
    #                   x=100,
    #                   y=55,
    #                   z=15,
    #                   xlength=1,
    #                   ylength=22,
    #                   zlength=22
    #                   )
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector2",
    #                   x=100,
    #                   y=25,
    #                   z=15,
    #                   xlength=1,
    #                   ylength=22,
    #                   zlength=22
    #                   )

    grid.add_object(tff)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve.plot(axis="z",
               index=0,
               filepath=grid.folder)

    # # 绘制单模波导截面折射率分布并计算模式
    # solve._plot_(axis='x',
    #              index=20,
    #              filepath=grid.folder)
    #
    # # 计算这个截面处，波长1.55um，折射率3.47附近的10个模式
    # solve._calculate_mode(lam=1.55, neff=3.47, neigs=10)
    #
    # # 绘制计算的10个模式并保存
    # solve._draw_mode(neigs=10)
    #
    # # 计算各个模式的TEfraction，并保存图片
    # # solve._calculate_TEfraction(n_levels=6)
    # # 打印这些模式对应的有效折射率
    # print(solve.effective_index)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.visualize(z=0, showEnergy=True, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
