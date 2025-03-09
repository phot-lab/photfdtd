from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":
    background_index = 3.2

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=4e-6, grid_ylength=1.5e-6, grid_zlength=1, grid_spacing=10e-9,
                permittivity=background_index ** 2, foldername="waveguide_result")

    # 设置器件参数
    waveguide = Waveguide(
        xlength=1e-6, ylength=0.2e-6, zlength=1, refractive_index=3.47638, name="Waveguide",
        grid=grid
    )

    # 添加波导
    grid.add_object(waveguide)
    grid.save_fig()

    # 接下来我们绘制z=0截面的折射率分布，并计算在该截面处的五个模式
    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制截面折射率分布
    solve.plot()

    # Now we can calculate modes
    data = solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=10,
                                x_boundary_low="pml",
                                y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                y_thickness_low=0.5e-6,
                                y_thickness_high=0.5e-6,
                                background_index=background_index)


    # # 也可以是场的相位、实部或虚部
    # solve.draw_mode(filepath=solve.filepath,
    #                 data=data,
    #                 content="phase")
    # solve.draw_mode(filepath=solve.filepath,
    #                 data=data,
    #                 content="real_part")
    # solve.draw_mode(filepath=solve.filepath,
    #                 data=data,
    #                 content="imaginary_part")

    # 如果保存了模式的数据，则可以读取它再绘制模式场
    Solve.save_mode(solve.filepath, data)

    # Draw the modes 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="real_part")
    #
    # data_from_saved_modes = Solve.read_mode(solve.filepath)
    #
    # Solve.draw_mode(filepath=solve.filepath, data=data_from_saved_modes, content="real_part")
