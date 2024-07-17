import utils
from photfdtd import TFF, Grid, Solve

if __name__ == "__main__":
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.0

    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=10e-6, grid_spacing=grid_spacing,
                foldername="test_tff_gaussian",
                permittivity=background_index ** 2)

    # 制作一个11层厚，1550nm波长的增返膜
    tff = TFF(
        xlength=5e-6,
        ylength=1,
        x=3e-6,
        y=0,
        z=4.8e-6,
        name="TFF",
        layers=11,
        axis="z",
        low_index=1.35,
        high_index=2.35,
        dh=0.16e-6,
        dl=0.28e-6,
        grid=grid
    )

    grid.set_source(source_type="linesource", wavelength=650e-9, name="source", z=8e-6, xlength=1e-6,
                    ylength=0, zlength=0, polarization="x", pulse_type="gaussian", pulse_length=10e-15,
                    offset=15e-15)
    grid.set_detector(detector_type='linedetector',
                      x_start=2.7e-6, y_start=0e-6, z_start=3e-6,
                      x_end=3.2e-6, y_end=0e-6, z_end=3e-6,
                      name='detector1')

    grid.add_object(tff)
    grid.plot_n()
    grid.save_fig()

    grid.run(time=100e-15)
    grid.save_fig(show_energy=True)
    # # 保存仿真结果
    grid.save_simulation()
    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0)
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    wl_start = 400e-9
    wl_end = 1800e-9
    source_data = grid.calculate_source_profile()
    Grid.compute_frequency_domain(grid=grid, name_det="detector1", wl_start=wl_start, wl_end=wl_end, index=5)
    # # 读取仿真结果
    grid.calculate_Transmission(field_axis="x", wl_start=400e-9, wl_end=1800e-9)


