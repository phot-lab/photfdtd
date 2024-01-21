import utils
from photfdtd import Ysplitter, Grid, Solve, Taper

if __name__ == "__main__":
    background_index = 1.4447

    # 设置 grid 参数
    grid = Grid(grid_xlength=400, grid_ylength=200, grid_zlength=1, grid_spacing=20e-9,
                foldername="test_taper_2D", permittivity=background_index ** 2)

    # 设置器件参数
    taper = Taper(xlength=300, ylength=25, zlength=1, direction=1, width=6,
                  name="taper",
                  refractive_index=3.47, grid=grid)

    grid.add_object(taper)
    # grid.save_fig(axis="x", axis_number=51)
    # grid.save_fig(axis="x", axis_number=149)
    grid.save_fig(axis="z", axis_number=0)
    # 创建solve对象
    # solve_fiber_side = Solve(grid=grid,
    #                          axis='x',
    #                          index=51,
    #                          filepath=grid.folder)
    grid.set_source(source_type="linesource", wavelength=1550e-9, name="source", x=7.1e-6, y=2e-6, z=0,
                    xlength=0, ylength=30, zlength=0, polarization="y")

    # run the FDTD simulation 运行仿真
    grid.run()

    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="y", axis="z", axis_index=0, folder=grid.folder)
    # Grid.plot_field(grid=grid, field="E", field_axis="y", axis="x", axis_index=51, folder=grid.folder)
    # Grid.plot_field(grid=grid, field="E", field_axis="y", axis="x", axis_index=149, folder=grid.folder)

    # grid.save_fig(axis="x", axis_number=51, show_energy=True)
    # grid.save_fig(axis="x", axis_number=149, show_energy=True)
    grid.save_fig(axis="z", axis_number=0, show_energy=True)

    # # 绘制任一截面折射率分布
    # solve_fiber_side.plot()
    #
    # # Now we can calculate modes
    # data_fiber_side = solve_fiber_side.calculate_mode(lam=1550e-9, neff=2, neigs=20,
    #                                                   x_boundary_low="pml",
    #                                                   y_boundary_low="pml",
    #                                                   x_boundary_high="pml",
    #                                                   y_boundary_high="pml",
    #                                                   background_index=background_index)
    #
    # # Draw the modes 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    # solve_fiber_side.draw_mode(filepath=solve_fiber_side.filepath,
    #                            data=data_fiber_side,
    #                            content="amplitude")
    #
    # solve_wg_side = Solve(grid=grid,
    #                       axis='x',
    #                       index=148,
    #                       filepath=grid.folder)
    #
    # # 绘制任一截面折射率分布
    # solve_wg_side.plot()
    #
    # # Now we can calculate modes
    # data_wg_side = solve_wg_side.calculate_mode(lam=1550e-9, neff=3.47, neigs=5,
    #                                             x_boundary_low="pml",
    #                                             y_boundary_low="pml",
    #                                             x_boundary_high="pml",
    #                                             y_boundary_high="pml",
    #                                             background_index=background_index)
    #
    # # Draw the modes 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    # solve_wg_side.draw_mode(filepath=solve_wg_side.filepath + "\\wg_side",
    #                         data=data_wg_side,
    #                         content="amplitude")
