import utils
from photfdtd import Mmi, Grid, Solve

if __name__ == "__main__":
    n = 1  # 输入端口数
    m = 2  # 输出端口数
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.0

    mmi = Mmi(
        xlength=71,
        ylength=56,
        zlength=20,
        We=56,
        x=60,
        y=40,
        z=15,
        name="mmi",
        refractive_index=3.47,
        n=n,
        m=m,
        width_port=25,
        width_wg=20,
        l_port=0,
        ln=20,
        lm=20,
        background_index=background_index
    )

    grid = Grid(grid_xlength=120, grid_ylength=80, grid_zlength=30, grid_spacing=grid_spacing, total_time=500,
                pml_width_x=10,
                pml_width_y=5, pml_width_z=1, foldername="test_mmi",
                permittivity=background_index ** 2)

    # for i in range(mmi.n):
    #     grid.set_source(
    #         x=9,
    #         xlength=0,
    #         y=mmi.ports_in[i].y,
    #         ylength=mmi.ports_in[i].ylength,
    #         source_type="linesource",
    #         period=1550e-9 / 299792458,
    #     )

    grid.set_source(
        x=15, xlength=1, y=40, ylength=18, z=15, zlength=18, source_type="planesource",
        period=1550e-9 / 299792458,
        name="source"
    )

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector1",
                      x=100,
                      y=55,
                      z=15,
                      xlength=1,
                      ylength=22,
                      zlength=22
                      )
    grid.set_detector(detector_type="blockdetector",
                      name="detector2",
                      x=100,
                      y=25,
                      z=15,
                      xlength=1,
                      ylength=22,
                      zlength=22
                      )


    grid.add_object(mmi)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve._plot_(axis='z',
                 index=15,
                 filepath=grid.folder)

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


    # 运行仿真
    grid.run()


    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.save_fig(axis="z",
                  axis_number=15)
    grid.save_fig(axis="x",
                  axis_number=20)
    grid.save_fig(axis="x",
                  axis_number=60)
    grid.save_fig(axis="x",
                  axis_number=100)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
