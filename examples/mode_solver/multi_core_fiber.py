from photfdtd import Fiber, Grid, Solve

if __name__ == "__main__":
    # 多芯光纤模式分析
    # 多芯光纤，参数：
    # 包层折射率：1.4437
    # 纤芯折射率：1.4504
    # 纤芯半径：2um
    # 芯距：7um
    # 分布：六边形
    # Pml边界厚度：3um
    # 波长：1.55um

    background_index = 1.4437
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=200e-9,
                foldername="test_multi_core_fiber",
                permittivity=background_index ** 2)
    # 在六边形的六个角和中心放置纤芯
    fiber1 = Fiber(length=1, x=100, y=100, z=0, radius=[10], refractive_index=[1.4504], name='fiber1', axis='z',
                  grid=grid)
    fiber2 = Fiber(length=1, x=100 + 18, y=100 - 30, z=0, radius=[10], refractive_index=[1.4504], name='fiber2', axis='z',
                   grid=grid)
    fiber3 = Fiber(length=1, x=100 - 18, y=100 - 30, z=0, radius=[10], refractive_index=[1.4504], name='fiber3', axis='z',
                   grid=grid)
    fiber4 = Fiber(length=1, x=100 - 35, y=100, z=0, radius=[10], refractive_index=[1.4504], name='fiber4', axis='z',
                   grid=grid)
    fiber5 = Fiber(length=1, x=100 - 18, y=100 + 30, z=0, radius=[10], refractive_index=[1.4504], name='fiber5', axis='z',
                   grid=grid)
    fiber6 = Fiber(length=1, x=100 + 18, y=100 + 30, z=0, radius=[10], refractive_index=[1.4504], name='fiber6', axis='z',
                   grid=grid)
    fiber7 = Fiber(length=1, x=100 + 35, y=100, z=0, radius=[10], refractive_index=[1.4504], name='fiber7', axis='z',
                   grid=grid)



    # 添加fiber到grid
    grid.add_object(fiber1)
    grid.add_object(fiber2)
    grid.add_object(fiber3)
    grid.add_object(fiber4)
    grid.add_object(fiber5)
    grid.add_object(fiber6)
    grid.add_object(fiber7 )

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis="z",
                  filepath=grid.folder,
                  index=0
                  )

    # 绘制折射率分布
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data = solve.calculate_mode(lam=1550e-9, neff=1.4504, neigs=20,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_low=15,
                                y_thickness_low=15,  x_thickness_high=15,
                                y_thickness_high=15,
                                background_index=background_index)

    Solve.draw_mode(filepath=solve.filepath, data=data, content="amplitude")
    # Solve.draw_mode(filepath=solve.filepath, data=data, content="real_part")
    # Solve.draw_mode(filepath=solve.filepath, data=data, content="imaginary_part")
    # Solve.draw_mode(filepath=solve.filepath, data=data, content="phase")

    # Solve.save_mode(solve.filepath, data)




