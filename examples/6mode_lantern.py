from photfdtd import Grid, Lantern_6Mode, Solve


if __name__ == "__main__":
    # 在这里实例化 Lantern_6Mode 对象并添加到 grid 中
    taper_ratio=0.4
    background_index = 1.438
    grid = Grid(grid_xlength=125e-6*taper_ratio, grid_ylength=125e-6*taper_ratio, grid_zlength=1, grid_spacing=312.5e-9*taper_ratio,
                foldername="test_lantern_6mode_0.4",
                permittivity=background_index ** 2)


    # 实例化 Lantern_6Mode 对象
    lantern_1= Lantern_6Mode(
        length=1,
        r_LP01=4.25e-6,
        r_LP11a=3.75e-6,
        r_LP11b=3.5e-6,
        r_LP21a=3.25e-6,
        r_LP21b=3.1e-6,
        r_LP02=2.5e-6,
        r=34.5e-6,
        taper_ratio=taper_ratio,
        n_LP01=1.45,
        n_LP11a=1.45,
        n_LP11b=1.45,
        n_LP21a=1.45,
        n_LP21b=1.45,
        n_LP02=1.45,
        n_cladding=1.444,
        r_cladding=55e-6,
        axis="z",
        grid=grid,
        priority=[1, 1, 1, 1, 1, 1, 1],
        name="lantern_6mode"
    )

    # 往 grid 里添加 fiber
    grid.add_object(lantern_1)

    # 创建 solve 对象
    solve = Solve(grid=grid,
                  axis="z",
                  filepath=grid.folder,
                  index=0
                  )

    # 绘制折射率分布
    solve.plot()
    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data = solve.calculate_mode(lam=1550e-9, neff=1.45, neigs=12,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_low=15,
                                y_thickness_low=15,  x_thickness_high=15,
                                y_thickness_high=15,
                                background_index=background_index)

    Solve.draw_mode(filepath=solve.filepath, data=data, content="amplitude")

