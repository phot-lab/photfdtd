import utils
from photfdtd import Mmi, Grid, Index

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    n = 1  # 输入端口数
    m = 5  # 输出端口数
    grid_spacing = 100e-9  # 空间步长

    grid = Grid(grid_xlength=14e-6, grid_ylength=1, grid_zlength=75e-6, grid_spacing=grid_spacing,
                foldername="test_star",
                permittivity=1. ** 2)

    star = Mmi(
        xlength=10e-6,
        ylength=1,
        zlength=43.88e-6 - 0.5e-6,
        name="star_coupler",
        refractive_index=index_Re_Si,
        n=n,
        m=m,
        width_port=0.8e-6,
        width_wg=0.4e-6,
        l_port=5e-6,
        ln=10e-6,
        lm=10e-6,
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

    grid.set_source(source_type="linesource", wavelength=1550e-9, axis="z", name="source", polarization="x",
                    x_start=6.7e-6, x_end=7.3e-6, z_start=5e-6, z_end=5e-6)

    # 设置监视器
    # grid.set_detector(detector_type='linedetector',
    #                   x_start=2e-6, y_start=0e-6, z_start=9.2e-6,
    #                   x_end=2.5e-6, y_end=0e-6, z_end=9.2e-6,
    #                   name='detector1')

    grid.add_object(star)
    grid.save_fig()
    grid.plot_n()

    grid.run()
    grid.save_simulation()
    #
    # # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, vmax=.5, vmin=-.5)
    grid.save_fig(axis="y",
                  axis_number=0,
                  show_energy=True)
    # # 读取仿真结果
    # data = Grid.read_simulation(folder=grid.folder)
