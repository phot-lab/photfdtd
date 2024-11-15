import utils
from photfdtd import DirectionalCoupler, Grid, Solve

if __name__ == "__main__":
    background_index = 1.4555

    grid = Grid(grid_xlength=8e-6, grid_ylength=1, grid_zlength=12e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_dc_2D")

    dc = DirectionalCoupler(
        xlength_sbend=1.8e-6,
        zlength_sbend=3e-6,
        ylength=1,
        width_1=0.45e-6,
        width_2=0.4e-6,
        name="dc",
        refractive_index=3.45,
        zlength_rectangle=4e-6,
        gap=0.06e-6,
        grid=grid
    )
    #
    grid.set_source(source_type="linesource", wavelength=1550e-9,
                    x_start=5.4e-6, y_start=0, z_start=0.9e-6,
                    x_end=6e-6, y_end=0, z_end=0.9e-6, pulse_type="gaussian",
                    polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=2e-6,y_start=0,z_start=11e-6,
                      x_end=2.5e-6,y_end=0,z_end=11e-6,
                      name='detector1')
    grid.set_detector(detector_type='linedetector',
                      x_start=5.5e-6, y_start=0, z_start=11e-6,
                      x_end=6e-6, y_end=0, z_end=11e-6,
                      name='detector2')

    grid.add_object(dc)
    grid.plot_n(grid=grid, axis="y", axis_index=0)
    grid.save_fig(axis="y", axis_number=0)

    grid.run(time=300e-15)

    # # 保存仿真结果
    grid.save_simulation()
    # grid = Grid.read_simulation(folder=grid.folder)
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder,
                    vmax=1, vmin=-1)
    grid.detector_profile()
    source_data = grid.calculate_source_profile()
    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")

    wl, spectrum1 = grid.compute_frequency_domain(grid=grid, name_det="detector1", wl_start=1300e-9, wl_end=1800e-9)
    wl, spectrum2 = grid.compute_frequency_domain(grid=grid, name_det="detector2", wl_start=1300e-9, wl_end=1800e-9)
    wl, spectrum_source = grid.compute_frequency_domain(grid=grid, input_data=source_data[:, 15, 0], wl_start=1300e-9, wl_end=1800e-9)
    grid.calculate_Transmission(field_axis="x", wl_start=1300e-9, wl_end=1800e-9, detector_name="detector1")
    grid.calculate_Transmission(field_axis="x", wl_start=1300e-9, wl_end=1800e-9, detector_name="detector2")


