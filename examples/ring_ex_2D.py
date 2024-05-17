import utils
from photfdtd import Ring, Grid

if __name__ == "__main__":
    background_index = 1.4447

    grid = Grid(grid_xlength=7e-6, grid_ylength=1, grid_zlength=7e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_ring_2D")

    ring = Ring(outer_radius=100 * 20e-9, ylength=1 * 20e-9, width_s=300e-9, width_r=400e-9, length=50 * 20e-9,
                gap=5 * 20e-9,
                name="ring", refractive_index=3.47, direction=1, grid=grid)

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, pulse_type="None", x=1.24e-6, y=0, z=1e-6,
                    xlength=21, ylength=1, zlength=1, polarization="x")


    grid.set_detector(detector_type='linedetector',
                      x_start=1.2e-6, y_start=0e-6, z_start=4e-6,
                      x_end=1.4e-6, y_end=0e-6, z_end=4e-6,
                      name='detector1')

    grid.add_object(ring)
    grid.save_fig(axis="y", axis_number=0)
    grid.plot_n(axis="y", axis_index=0)

    grid.run()

    grid.save_simulation()
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder,
                    vmax=2, vmin=-2)

    # 读取仿真结果
    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
