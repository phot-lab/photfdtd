import utils
from photfdtd import Mmi, Grid, Solve

if __name__ == "__main__":
    n = 3  # 输入端口数
    m = 2  # 输出端口数
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.4447

    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=10e-6, grid_spacing=grid_spacing, foldername="test_mmi_2D",
                permittivity=background_index ** 2)

    mmi = Mmi(
        xlength=2e-6,
        ylength=1,
        zlength=3e-6,
        We=100 * grid_spacing,
        name="mmi",
        refractive_index=3.47,
        n=n,
        m=m,
        # x=225,
        width_port=25,
        width_wg=20,
        l_port=1e-6,
        ln=1e-6,
        lm=1e-6,
        grid=grid
    )



    # for i in range(mmi.n):
    #     grid.set_source(
    #         x=9,
    #         xlength=0,
    #         y=mmi.ports_in[i].y,
    #         ylength=mmi.ports_in[i].ylength,
    #         source_type="linesource",
    #         period=1550e-9 / 299792458,
    #     )

    # grid.set_source(source_type="linesource", period=1550e-9 / 299792458, name="source", x=0.9e-6, y=3e-6, z=0, xlength=1,
    #                 ylength=25, zlength=1, polarization="y")

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector1",
    #                   x=100,
    #                   y=55,
    #                   z=15,
    #                   xlength=1,
    #                   ylength=22,
    #                   zlength=22
    #                   )
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector2",
    #                   x=100,
    #                   y=25,
    #                   z=15,
    #                   xlength=1,
    #                   ylength=22,
    #                   zlength=22
    #                   )

    grid.add_object(mmi)

    grid.save_fig(axis="y",
                  axis_number=0)

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='y',
                  index=0,
                  filepath=grid.folder)

    # 绘制任一截面折射率分布
    solve.plot()

    # # 绘制单模波导截面折射率分布并计算模式
    # solve._plot_(axis='x',
    #              index=20,
    #              filepath=grid.folder)
    #
    # # 计算这个截面处，波长1.55um，折射率3.47附近的10个模式
    # solve._calculate_mode(lam=1.55, neff=3.47, neigs=10)
    #
    # # 绘制计算的10个模式并保存
    # solve._draw_mode(neigs=10)
    #
    # # 计算各个模式的TEfraction，并保存图片
    # # solve._calculate_TEfraction(n_levels=6)
    # # 打印这些模式对应的有效折射率
    # print(solve.effective_index)
    grid.run()

    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="y", axis="z", axis_index=0, folder=grid.folder,
                    vmax=1)
    grid.save_fig(axis="z",
                  axis_number=0,
                  show_energy=True)


