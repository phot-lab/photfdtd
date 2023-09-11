from photfdtd import Sbend, Grid, Solve, constants


if __name__ == "__main__":

    background_index=1.0

    # 设置波导参数
    sbend = Sbend(
        xlength=200, ylength=100, zlength=20, x=100, y=75, z=13, direction=-1, width=20, refractive_index=3.47, name="sbend",
        background_index=background_index
    )

    # 设置 grid 参数
    grid = Grid(grid_xlength=200, grid_ylength=150, grid_zlength=25, grid_spacing=20e-9,
                total_time=600,
                pml_width_x=20,
                pml_width_y=10,
                pml_width_z=1,
                foldername="test_sbend",
                permittivity=background_index ** 2)

    # 设置光源
    grid.set_source(source_type="planesource",
                    period=1550e-9/constants.c,
                    name="source",
                    x=30,
                    y=110,
                    z=13,
                    xlength=1,
                    ylength=20,
                    zlength=20
                    )

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=175,
                      y=40,
                      z=13,
                      xlength=1,
                      ylength=20,
                      zlength=20
                      )

    # 添加器件
    grid.add_object(sbend)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制截面
    solve._plot_(axis='z',
                 index=13,
                 filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.save_fig(axis="z",
                  axis_number=13)
    grid.save_fig(axis="y",
                  axis_number=80)
    grid.save_fig(axis="x",
                  axis_number=100)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)