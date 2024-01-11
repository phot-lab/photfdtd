from photfdtd import Grid, Solve, Fiber

if __name__ == "__main__":
    background_index = 1.445
    grid = Grid(grid_xlength=350, grid_ylength=210, grid_zlength=1, grid_spacing=250e-9,
                permittivity=background_index ** 2,
                foldername="test_optical_crystal")

    for i in range(6):
        # 行
        for j in range(6 + i):
            # 列
            if i == 5 and j == 5:
                continue
            else:
                circle = Fiber(length=1, x=105 + j * 28 - i * 14, y=25 + i * 16, z=0, radius=[4], refractive_index=[1],
                               name="%i%i" % (i, j), axis='z', background_index=background_index)
            grid.add_object(circle)

    for i in range(5):
        for j in range(6 + i):
            circle = Fiber(length=1, x=105 + j * 28 - i * 14, y=185 - i * 16, z=0, radius=[4], refractive_index=[1],
                           name="up^%i%i" % (i, j), axis='z', background_index=background_index)
            grid.add_object(circle)

    # clad = Fiber(length=1, x=180, y=105, z=0, radius=[160], refractive_index=[1.445],
    #              name="clad", axis='z')

    core = Fiber(length=1, x=175, y=105, z=0, radius=[12], refractive_index=[1.45],
                 name="core", axis='z', background_index=background_index)

    # grid.add_object(clad)
    grid.add_object(core)
    # 创建solve对象，
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)
    # 绘制折射率截面
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率1.45附近的10个模式
    data = solve.calculate_mode(lam=1.55, neff=1.45, neigs=2,
                                x_boundary_low="zero", y_boundary_low="zero",
                                x_boundary_high="zero",
                                y_boundary_high="zero",
                                x_thickness_low=15,
                                y_thickness_low=15, x_thickness_high=15,
                                y_thickness_high=15)

    # 绘制图像并保存
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="amplitude")
