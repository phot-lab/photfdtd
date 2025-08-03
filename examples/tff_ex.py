from photfdtd import TFF, Grid, Solve, fdtd
fdtd.set_backend("numpy")

if __name__ == "__main__":
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.0
    #
    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=10e-6, grid_spacing=grid_spacing,
                permittivity=background_index ** 2, foldername="test_tff_gaussian")

    tff = TFF(
        xlength=5e-6,
        ylength=1,
        x=3e-6,
        y=0,
        z=1e-6,
        name="TFF",
        layers=30,
        axis="z",
        low_index=1.,
        high_index=2.35,
        dh=0.16e-6,
        dl=0.28e-6,
        grid=grid
    )

    grid.set_source(source_type="linesource", wavelength=650e-9, name="source", z=8e-6, xlength=1e-6,
                    ylength=0, zlength=0, polarization="x", pulse_type="gaussian", pulse_length=10e-15,
                    offset=15e-15)
    grid.set_detector(detector_type='linedetector',
                      x_start=2.7e-6, y_start=0e-6, z_start=1e-6,
                      x_end=3.2e-6, y_end=0e-6, z_end=1e-6,
                      name='detector1')

    grid.add_object(tff)
    grid.plot_n()
    grid.save_fig()

    grid.run(save=True)

    grid.visualize()



