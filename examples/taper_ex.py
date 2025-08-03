from photfdtd import Grid, Taper, fdtd
fdtd.set_backend("numpy")

if __name__ == "__main__":
    background_index = 1.4447

    # 设置 grid 参数
    grid = Grid(grid_xlength=4e-6, grid_ylength=4e-6, grid_zlength=4e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_taper")

    # 设置器件参数
    taper = Taper(xlength_upper=2000e-9, xlength_lower=400e-9, ylength=500e-9, zlength=2e-6,
                  name="taper", refractive_index=3.47, grid=grid)

    grid.add_object(taper)
    grid.save_fig(axis="x", axis_index=51)
    grid.save_fig(axis="x", axis_index=149)
    grid.save_fig(axis="z", axis_index=100)

    grid.set_source(source_type="planesource", wavelength=1550e-9, name="source",
                    x=None, y=None, z=1e-6,
                    axis="z",
                    xlength=400e-9, ylength=500e-9, zlength=0, polarization="x")

    # run the FDTD simulation 运行仿真
    grid.run(time=1000, save=True)
    grid.visualize()
    
    # 绘制仿真结束时刻空间场分布
    grid.plot_field(field="E", field_axis="y", axis="z", axis_index=0, folder=grid.folder)
    grid.plot_field(field="E", field_axis="y", axis="x", axis_index=51, folder=grid.folder)
    grid.plot_field(field="E", field_axis="y", axis="x", axis_index=149, folder=grid.folder)

    grid.save_fig(axis="x", axis_index=51, show_energy=True)
    grid.save_fig(axis="x", axis_index=149, show_energy=True)
    grid.save_fig(axis="z", axis_index=100, show_energy=True)

    # # 创建solve对象
    # solve_fiber_side = Solve(grid=grid,
    #                          axis='x',
    #                          index=51,
    #                          filepath=grid.folder)

    # # 绘制任一截面折射率分布
    # solve_fiber_side.plot()
    #
    # # Now we can calculate modes
    # data_fiber_side = solve_fiber_side.calculate_mode(lam=1550e-9, neff=1.8, neigs=20,
    #                                                   x_boundary_low="pml",
    #                                                   y_boundary_low="pml",
    #                                                   x_boundary_high="pml",
    #                                                   y_boundary_high="pml",
    #                                                   x_thickness_low=30,
    #                                                   y_thickness_low=30, x_thickness_high=30,
    #                                                   y_thickness_high=30,
    #                                                   background_index=background_index)
    #
    # # Draw the modes 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    # solve_fiber_side.draw_mode(filepath=solve_fiber_side.filepath + "\\fiber_side",
    #                            data=data_fiber_side,
    #                            content="amplitude")
    #
    # # solve_wg_side = Solve(grid=grid,
    # #                       axis='x',
    # #                       index=148,
    # #                       filepath=grid.folder)
    # #
    # # # 绘制任一截面折射率分布
    # # solve_wg_side.plot()
    # #
    # # # Now we can calculate modes
    # # data_wg_side = solve_wg_side.calculate_mode(lam=1550e-9, neff=2.75, neigs=20,
    # #                                             x_boundary_low="pml",
    # #                                             y_boundary_low="pml",
    # #                                             x_boundary_high="pml",
    # #                                             y_boundary_high="pml",
    # #                                             background_index=background_index)
    # #
    # # # Draw the modes 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    # # solve_wg_side.draw_mode(filepath=solve_wg_side.filepath + "\\wg_side",
    # #                         data=data_wg_side,
    # #                         content="amplitude")
