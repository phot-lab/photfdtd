from photfdtd import Grid, Lantern_3Mode, Solve
import matplotlib.pyplot as plt


if __name__ == "__main__":
    """
    三模光子灯笼在拉锥比为0.16时的截面模式分析：
    工作波长：1550nm
    各参数设置：
    - 单模光纤纤芯折射率：1.4482
    - 包层折射率：1.444
    - 套管（环境）折射率：1.438
    - 包层半径：62.5μm
    - 各纤芯之间的距离：42μm
    - 用于激励不同模式的单模光纤纤芯半径：
      LP01模式：5.5μm
      LP11a模式：4.325μm
      LP11b模式：3.275μm
    """
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

    # 往 grid 里添加lantern
    grid.add_object(lantern)
    grid.save_fig()
    # 创建solve对象
    solve = Solve(grid=grid,
                  axis="z",
                  filepath=grid.folder,
                  index=0
                  )
    solve.plot()
     # 计算这个截面处，波长1.55um，折射率1.4482附近的2个模式，边界条件选择在四个方向上都是pml，
    data = solve.calculate_mode(lam=1550e-9, neff=1.4482, neigs=2,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                background_index=background_index)
    # 绘制模式场，我们选择绘制amplitude，即幅值
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="amplitude",
                    number=30)



