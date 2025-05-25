from photfdtd import Grid, Lantern_3Mode, Solve
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # 设置拉锥比和背景折射率
    taper_ratio=0.16
    background_index = 1.4398
    #设置grid参数
    grid = Grid(grid_xlength=160e-6, grid_ylength=160e-6, grid_zlength=1, grid_spacing=600e-9,
                foldername="test_lantern_3_0.16",
                permittivity=background_index ** 2)


    # 实例化 Lantern_3Mode 对象
    lantern = Lantern_3Mode(
        length=1,
        r_LP01=5.5e-6,
        r_LP11a=4.325e-6,
        r_LP11b=3.275e-6,
        distance=42e-6,
        taper_ratio=taper_ratio,
        n_LP01=1.4482,
        n_LP11a=1.4482,
        n_LP11b=1.4482,
        n_cladding=1.444,
        r_cladding=62.5e-6,
        axis="z",
        grid=grid,
        priority=[1, 1, 1, 1],
        name="lantern_3mode"
    )

    # 往 grid 里添加fiber
    grid.add_object(lantern)
    grid.save_fig()
    # 创建solve对象
    solve = Solve(grid=grid,
                  axis="z",
                  filepath=grid.folder,
                  index=0
                  )
    solve.plot()
     # 计算这个截面处，波长1.55um，折射率1.4482附近的6个模式，边界条件选择在四个方向上都是pml，
    data = solve.calculate_mode(lam=1550e-9, neff=1.4482, neigs=2,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                background_index=background_index)
    TE_fractions = solve.calculate_TEfraction(data, axis='z', n_levels=2)
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="amplitude",
                    number=30,TE_fractions=TE_fractions )
    #绘制模式场，我们选择绘制amplitude，即幅值
    solve.draw_mode(filepath=solve.filepath, data=data, content="amplitude")

