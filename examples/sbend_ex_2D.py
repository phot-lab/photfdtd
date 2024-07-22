import photfdtd.fdtd.constants as constants

from photfdtd import Sbend, Grid, Solve, Waveguide

if __name__ == "__main__":
    background_index = 1.4447

    # 设置 grid 参数
    grid = Grid(grid_xlength=200 * 20e-9, grid_ylength=1, grid_zlength=8000e-9, grid_spacing=20e-9,
                foldername="test_sbend_2D",
                permittivity=background_index ** 2,
                )

    # 设置波导参数
    sbend = Sbend(
        xlength=100 * 20e-9,
        ylength=1,
        zlength=150 * 20e-9,
        x=2e-6,
        z=3e-6,
        direction=1,
        width=20 * 20e-9,
        refractive_index=3.45,
        name="sbend",
        grid=grid,
    )

    waveguide = Waveguide(
        xlength=0.4e-6, ylength=1, zlength=1.5e-6, x=2.8e-6, y=0, z=5.25e-6, refractive_index=3.45, name="Waveguide", grid=grid
    )

    # 添加器件
    grid.add_object(sbend)
    grid.save_fig(axis="y", axis_index=0)
    grid.plot_n(grid=grid, axis="y", axis_index=0)


    grid.add_object(waveguide)

    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source",x=1.2e-6, y=0, z=1.4e-6,
                    xlength=500e-9, ylength=1, zlength=1, polarization="x")

    grid.save_fig(axis="y", axis_number=0)

    # 设置监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector",
                      x=2.8e-6,
                      y=0,
                      z=4.5e-6,
                      xlength=0.4e-6,
                      ylength=1,
                      zlength=1
                      )


    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='y',
                  index=0,
                  filepath=grid.folder)

    # 绘制截面
    solve.plot()

    # 运行仿真
    grid.run()
    grid.save_simulation()
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder, vmin=-1, vmax=1)
    grid.save_fig(axis="y", axis_number=0, show_energy=True)

    # 如果添加了监视器，还可以绘制某一点时域场变化曲线，这里选择index=30即监视器中心
    Grid.plot_fieldtime(folder=grid.folder, grid=grid, field_axis="z", index=10, name_det="detector")

    # 绘制频谱
    Grid.compute_frequency_domain(grid=grid, wl_start=1000e-9, wl_end=2000e-9, name_det="detector",
                                  index=10, field_axis="x", field="E", folder=None)

