import utils
from photfdtd import Mmi, Grid, Solve

if __name__ == "__main__":
    n = 1  # 输入端口数
    m = 2  # 输出端口数
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.4447

    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=10e-6, grid_spacing=grid_spacing,
                foldername="test_mmi_2D",
                permittivity=background_index ** 2)

    mmi = Mmi(
        xlength=2e-6,
        ylength=1,
        zlength=4.2e-6,
        We=2.09e-6,
        name="mmi",
        refractive_index=3.47,
        n=n,
        m=m,
        width_port=25,
        width_wg=20,
        l_port=0,
        ln=1.7e-6,
        lm=2e-6,
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

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, name="source", z=1e-6, xlength=20,
                    ylength=0, zlength=1, polarization="x")

    # 设置监视器
    grid.set_detector(detector_type='linedetector',
                      x_start=2e-6, y_start=0e-6, z_start=9.2e-6,
                      x_end=2.5e-6, y_end=0e-6, z_end=9.2e-6,
                      name='detector1')

    grid.add_object(mmi)
    grid.save_fig(axis="y", axis_number=0)
    grid.plot_n(axis="y", axis_index=0)

    grid.run()
    grid.save_simulation()

    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder,
                    vmax=2, vmin=-2)
    grid.save_fig(axis="y",
                  axis_number=0,
                  show_energy=True)
    # 读取仿真结果
    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="z", field="E", index=5, name_det="detector1")