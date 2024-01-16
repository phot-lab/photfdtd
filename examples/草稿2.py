from photfdtd import Hexagonal_PC, Grid, Solve, Fiber

if __name__ == "__main__":
    background_index = 1.445

    # 设置器件参数
    pc = Hexagonal_PC(n_side=3, zlength=1, x=100, y=100, z=0, H_number=1, refractive_index=1, name="pc",
                      background_index=background_index, a=40, radius=10)

    core = Fiber(length=1, x=100, y=100, z=0, radius=[30], refractive_index=[1.45],
                 name="core", axis='z', background_index=background_index)

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=200e-9,
                foldername="test_Hexagonal_PC",
                permittivity=background_index ** 2)

    # 往 grid 里添加器件
    grid.add_object(pc)
    grid.add_object(core)

    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )
    solve.plot()

    grid_sliced = grid.slice_grid(x_slice=[100, 200], y_slice=[100, 200], z_slice=[0, 1])

    solve = Solve(grid=grid_sliced,
                  axis='z',
                  index=0,
                  filepath=grid_sliced.folder
                  )
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data = solve.calculate_mode(lam=1550e-9, neff=1.45, neigs=5,
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_high=15,
                                y_thickness_high=15)
    # data = solve.calculate_mode(lam=1550e-9, neff=1.45, neigs=2)

    # 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="amplitude")
