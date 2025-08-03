from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":
    # 矩形波导模式分析
    background_index = 1.444

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=4e-6, grid_ylength=4e-6, grid_zlength=1, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="waveguide_result")

    # 设置器件参数
    waveguide = Waveguide(
        xlength=600e-9, ylength=440e-9, zlength=1, refractive_index=3.476, name="Waveguide",
        grid=grid
    )

    # 添加波导
    grid.add_object(waveguide)
    grid.save_fig()


    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制截面折射率分布
    solve.plot()

    # 计算模式
    data = solve.calculate_mode(lam=1550e-9, neff=3.476, neigs=20,
                                x_boundary_low="pml",
                                y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                background_index=background_index)



    # 如果保存了模式的数据，则可以读取它再绘制模式场
    solve.save_mode(solve.filepath, data)

    # Draw the modes 接下来即可绘制模式场，我们选择绘制real_part，即实部。filepath为保存绘制的图片的路径，number箭头(电场方向）个数
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="real_part",number=30)

