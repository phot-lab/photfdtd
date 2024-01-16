from photfdtd import Hexagonal_PC, Grid, Solve

if __name__ == "__main__":
    background_index = 1.0

    # 设置器件参数

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=10e-9, total_time=1000,
                foldername="test_Hexagonal_PC",
                pml_width_x=25,
                pml_width_y=25,
                pml_width_z=0,
                permittivity=background_index ** 2)
    pc = Hexagonal_PC(n_side=7, zlength=1 * 10e-9, H_number=3, refractive_index=3.47, name="pc",
                      grid=grid, a=13 * 10e-9, radius=4 * 10e-9)

    # 往 grid 里添加器件
    grid.add_object(pc)

    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )

    # 绘制任一截面
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data = solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=5,
                                x_boundary_low="pml", y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_low=15,
                                y_thickness_low=15, x_thickness_high=15,
                                y_thickness_high=15)
