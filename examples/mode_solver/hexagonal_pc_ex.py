from photfdtd import Hexagonal_PC, Grid, Solve, Fiber, fdtd
fdtd.set_backend("numpy")

if __name__ == "__main__":
    #光子晶体光纤
    #环境（包层）折射率：1.4437
    #空气孔折射率：1.0
    #纤芯折射率：1.4504
    #空气孔间距a：8μm
    #空气孔半径：2μm
    #纤芯半径：5μm


    background_index = 1.4437

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=46000e-9, grid_ylength=40000e-9, grid_zlength=1, grid_spacing=200e-9,
                permittivity=background_index ** 2, foldername="Hexagonal_PC_result")
    # 设置器件参数，空气孔
    pc = Hexagonal_PC(n_side=3, zlength=1, number=2, refractive_index=1, name="pc",
                      grid=grid, a=40 * 200e-9, radius=10 * 200e-9)
    #纤芯
    core = Fiber(length=1, radius=[25 * 200e-9], refractive_index=[1.4504],
                 name="core", axis='z', grid=grid)

    # 往 grid 里添加器件
    grid.add_object(pc)
    grid.add_object(core)
    grid.plot_n(axis="z", axis_index=0)
    grid.save_fig(axis="z", axis_index=0)
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制z=0截面
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率1.45附近的20个模式，边界条件选择在四个方向上都是pml，厚度均为3μm
    data = solve.calculate_mode(lam=1550e-9, neigs=20, neff=1.4504,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_low=3e-6,
                                y_thickness_low=3e-6, x_thickness_high=3e-6,
                                y_thickness_high=3e-6,
                                background_index=background_index)
    # Draw the modes 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="amplitude")
