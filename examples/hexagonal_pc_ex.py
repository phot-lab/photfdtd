from photfdtd import Hexagonal_PC, Grid, Solve

if __name__ == "__main__":
    background_index = 1.0

    # 设置器件参数
    pc = Hexagonal_PC(n_side=7, zlength=1, x=100, y=100, z=0, H_number=3, refractive_index=3.47, name="pc",
                      background_index=background_index, a=13, radius=4)

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=10e-9, total_time=1000,
                foldername="test_Hexagonal_PC",
                pml_width_x=25,
                pml_width_y=25,
                pml_width_z=0,
                permittivity=background_index ** 2)

    # 往 grid 里添加器件
    grid.add_object(pc)

    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )

    # 绘制任一截面
    solve.plot()
