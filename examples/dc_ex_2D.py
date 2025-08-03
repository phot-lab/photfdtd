import photfdtd.fdtd
from photfdtd import DirectionalCoupler, Grid
photfdtd.fdtd.set_backend("torch.cuda")

if __name__ == "__main__":
    background_index = 1.4555
    # TODO: PML边界似乎出了点问题，不能吸收光
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
    grid.set_PML(pml_width=1.5e-6)
    grid.set_source(source_type="linesource", wavelength=1550e-9,
                    x_start=5.4e-6, y_start=0, z_start=1.6e-6,
                    x_end=6e-6, y_end=0, z_end=1.6e-6, pulse_type="gaussian",
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
    grid.plot_n(axis="y", axis_index=0)
    grid.save_fig(axis="y", axis_index=0)

    grid.run(time=300e-15, save=True, animate=True)

    # grid = Grid.read_simulation(folder=grid.folder)
    grid.visualize()


