from photfdtd import Fiber, Grid, Solve

if __name__ == "__main__":
    background_index = 1.0

    fiber = Fiber(length=1, x=70, y=0, z=70, radius=[10, 40], refractive_index=[3.47, 1.45], name='fiber', axis='y',
                  background_index=background_index)

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=140, grid_ylength=1, grid_zlength=140, grid_spacing=11e-9, total_time=1,
                foldername="test_fiber",
                permittivity=background_index ** 2)

    # 往 grid 里添加一个器件
    grid.add_object(fiber)

    # 创建solve对象
    solve = Solve(grid=grid)

    solve._plot_(axis='y',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    grid.save_fig(axis="y",
                  axis_number=0)
