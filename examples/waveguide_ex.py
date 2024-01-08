from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=400, ylength=20, zlength=20, x=200, y=30, z=20, refractive_index=3.47, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=60, grid_zlength=40,
                grid_spacing=20e-9,
                total_time=800,
                pml_width_x=80,
                pml_width_y=1,
                pml_width_z=1,
                permittivity=background_index ** 2,
                foldername="test_waveguide")

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置光源
    grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=100, y=30, z=20,
                    xlength=0, ylength=0, zlength=0)

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=240,
                      y=30,
                      z=20,
                      xlength=150,
                      ylength=40,
                      zlength=0
                      )

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=20,
                  filepath=grid.folder
                  )

    # 绘制任一截面折射率分布
    solve.plot()

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.save_fig(axis="x",
                  axis_number=200,
                  geo=solve.geometry)
    grid.save_fig(axis="z",
                  axis_number=20,
                  geo=solve.geometry)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
    # 绘制监视器范围内光场分布
    Grid.dB_map(folder="D:/Github_Clone/photfdtd/examples/test_waveguide", total_time=1600, data=data, axis="x-y",
                field_axis=0, field="E", name_det="detector", interpolation="spline16", save=True)
