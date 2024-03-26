import utils
from photfdtd import Waveguide, Arc, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.4447
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=6e-6, grid_spacing=20e-9,
                foldername="test_arc_2D",
                permittivity=background_index ** 2, )

    # 设置器件参数
    arc = Arc(outer_radius=2e-6, ylength=1, width=0.4e-6, refractive_index=3.47, name="arc", angle_phi=0, angle_psi=90,
              grid=grid, angle_unit=True)
    waveguide1 = Waveguide(
        xlength=2.2e-6, ylength=1, zlength=0.4e-6, x=2e-6, y=0, z=4.8e-6, refractive_index=3.47, name="Waveguide1", grid=grid
    )
    waveguide2 = Waveguide(
        xlength=0.4e-6, ylength=1, zlength=2.2e-6, x=4.8e-6, y=0, z=2e-6, refractive_index=3.47, name="Waveguide2", grid=grid
    )

    # 往 grid 里添加器件
    grid.add_object(arc)
    grid.add_object(waveguide1)
    grid.add_object(waveguide2)
    grid.save_fig(axis="y", axis_number=0)
    grid.plot_n(axis="y", axis_index=0)

    # 设置光源
    grid.set_source(source_type="pointsource", period=1550e-9 / constants.c, name="source", x=2.5e-6, y=0, z=4.8e-6,
                    xlength=0, ylength=0, zlength=0.2e-6, polarization="z", amplitude=1)

    grid.set_detector(detector_type='linedetector',
                      x_start=4.5e-6, y_start=0e-6, z_start=2.8e-6,
                      x_end=5e-6, y_end=0e-6, z_end=2.8e-6,
                      name='detector1')

    # 运行仿真
    grid.run()
    grid.save_simulation()

    # # 绘制仿真结束时刻空间场分布
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    Grid.plot_field(grid=grid, field="E", field_axis="z", axis="y", axis_index=0, folder=grid.folder, vmax=2)

    # 读取仿真结果
    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(folder=grid.folder, data=data, field="E", field_axis="z",
                        index=5, name_det="detector1")