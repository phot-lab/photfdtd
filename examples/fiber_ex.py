from photfdtd import Fiber, Grid, Solve, constants

if __name__ == "__main__":
    # 单模光纤模式分析
    # 单模光纤，参数：
    # 包层折射率：1.4437
    # 纤芯折射率：1.4504
    # 纤芯半径：4um
    # Pml边界厚度：3um
    # 波长：1.55um

    background_index = 1.4437

    fiber = Fiber(length=1, x=100, y=100, z=0, radius=[20], refractive_index=[1.4504], name='fiber', axis='z',
                  background_index=background_index)

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=200e-9,
                foldername="test_fiber", permittivity=background_index ** 2)

    # 往 grid 里添加fiber
    grid.add_object(fiber)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制折射率分布
    solve.plot(axis="z",
               filepath=grid.folder,
               index=0)

    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data = solve.calculate_mode(lam=1550e-9, neff=1.4504, neigs=2,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_low=15,
                                y_thickness_low=15,  x_thickness_high=15,
                                y_thickness_high=15)

    Solve.save_mode(solve.filepath, data)

    Solve.draw_mode(filepath=solve.filepath, data=data, content="amplitude")
    Solve.draw_mode(filepath=solve.filepath, data=data, content="real_part")
    Solve.draw_mode(filepath=solve.filepath, data=data, content="imaginary_part")
    Solve.draw_mode(filepath=solve.filepath, data=data, content="phase")


