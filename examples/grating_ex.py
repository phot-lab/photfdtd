from photfdtd import Grating, Grid, fdtd
fdtd.set_backend("numpy")

if __name__ == "__main__":
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.4447
    #
    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=10e-6, grid_spacing=grid_spacing,
                permittivity=background_index ** 2, foldername="test_grating")

    grt = Grating(
        xlength=5e-6,
        ylength=1,
        x=3e-6,
        y=0,
        z=4.8e-6,
        name="Grating",
        duty_cyle=0.6,
        period=400e-9,
        n_periods=5,
        axis="z",
        refractive_index=3.47,
        grid=grid
    )
    #
    grid.set_source(source_type="linesource", wavelength=650e-9, name="source", z=8e-6, xlength=1e-6,
                    ylength=0, zlength=0, polarization="x", pulse_type="gaussian", pulse_length=10e-15,
                    offset=15e-15)
    grid.set_detector(detector_type='linedetector',
                      x_start=2.7e-6, y_start=0e-6, z_start=3e-6,
                      x_end=3.2e-6, y_end=0e-6, z_end=3e-6,
                      name='detector1')
    #
    grid.add_object(grt)
    grid.plot_n()
    grid.save_fig()
    #
    grid.run(save=True)
    # # # 保存仿真结果
    grid.visualize()

    # for time in range(10):
    #     grid.detector_profile(timesteps=795+time)
    # Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0)
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    # wl_start = 500e-9
    # wl_end = 800e-9
    # source_data = grid.calculate_source_profile()
    # wl, spectrum_d = Grid.compute_frequency_domain(grid=grid, name_det="detector1", wl_start=wl_start, wl_end=wl_end, index=5)
    # wl, spectrum_s = grid.compute_frequency_domain(grid=grid, input_data=source_data[:, 25, 0], wl_start=wl_start, wl_end=wl_end)
    #
    # grid.calculate_Transmission(field_axis="x", wl_start=500e-9, wl_end=800e-9)


