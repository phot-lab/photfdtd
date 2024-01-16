import utils
from photfdtd import DirectionalCoupler, Grid, Solve, Analyse
import numpy as np
import matplotlib.pyplot as plt
if __name__ == "__main__":

    background_index = 1.455

    dc = DirectionalCoupler(
        xlength=125,
        ylength=65,
        zlength=1,
        x=100,
        y=100,
        z=0,
        direction=1,
        width=4,
        name="dc",
        refractive_index=3.47,
        xlength_rectangle=35,
        gap=1,
        background_index=background_index
    )

    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=50e-9, total_time=1000,
                pml_width_x=20,
                pml_width_y=20, pml_width_z=0,
                permittivity=background_index ** 2, foldername="test_frequency_domain")

    grid.set_source(
        x=dc.x, xlength=0, y=dc.y, ylength=dc.width, source_type="linesource", period=1550e-9 / 299792458, pulse=False
    )

    grid.set_detector(detector_type='linedetector',
                      x=dc.x, xlength=0, y=dc.y + dc.ylength - dc.width, ylength=dc.width, z=0, zlength=0,
                      name='detector_source')

    grid.add_object(dc)

    # 创建solve对象
    solve = Solve(grid=grid)

    solve.plot(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    grid.save_fig(axis="z", axis_number=0, animate=d)

    # 调用Analyse计算坡印亭矢量和功率,
    analyse = Analyse(E=grid._grid.detector_source.E, H=grid._grid.detector_source.H,
                      grid_spacing=grid._grid.grid_spacing)

    # print(analyse.P)
    # print(analyse.Power)

    t = np.linspace(0, 1000, 1000)
    plt.plot(t, analyse.Power["power_positive_x"], label='Px+')
    plt.plot(t, analyse.Power["power_negative_x"], label='Px-')
    plt.plot(t, analyse.Power["power_positive_y"], label='Py+')
    plt.plot(t, analyse.Power["power_negative_y"], label='Py-')
    plt.plot(t, analyse.Power["power_positive_z"], label='Pz+')
    plt.plot(t, analyse.Power["power_negative_z"], label='Pz-')# 绘制曲线，添加标签
    plt.title('Power Plot')  # 添加标题
    plt.xlabel('t')  # 添加x轴标签
    plt.ylabel('y')  # 添加y轴标签
    plt.legend()  # 添加图例
    plt.grid()  # 添加网格线
    plt.show()  # 显示图表



    #计算频域结果并绘图
    grid.compute_frequency_domain(wl_start=1.0, wl_end=2.0, input_data=np.array(grid._grid.detector_source.E)[:,2,2])
