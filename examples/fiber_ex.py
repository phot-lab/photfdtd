from photfdtd import Fiber, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    fiber = Fiber(length=100, x=50, y=50, z=50, radius=[10, 40], refractive_index=[3.47, 1.45], name='fiber', axis='y',
                  background_index=background_index)

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=100, grid_ylength=100, grid_zlength=100, grid_spacing=20e-9, total_time=500,
                foldername="test_fiber",
                pml_width_x=1,
                pml_width_y=10,
                pml_width_z=1,
                permittivity=background_index ** 2)

    # 往 grid 里添加一个器件
    grid.add_object(fiber)

    # 设置光源
    grid.set_source(source_type="planesource", period=1550e-9 / constants.c, name="source", x=50, y=15, z=50,
                    xlength=20, ylength=0, zlength=20)

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=50,
                      y=85,
                      z=50,
                      xlength=20,
                      ylength=0,
                      zlength=20
                      )

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve.plot()

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.visualize(x=50, showEnergy=True, show=True, save=True)
    grid.visualize(z=50, showEnergy=True, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)

