from photfdtd import Waveguide, Grid, Solve, Index, Sbend, Taper

if __name__ == "__main__":
    # set background index设置背景折射率
    background_index = 1.0
    index = Index(material="Si", wavelength=1.55)
    
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=100, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_rotation")

    # set waveguide设置器件参数
    waveguide = Waveguide(
        xlength=90, ylength=10, zlength=50, x=120, y=100, z=50, refractive_index=3.47, name="waveguide",
        grid=grid
    )
    waveguide.rotate_Z(angle=20, center=[100, 100, 50])
    grid.add_object(waveguide)

    grid.save_fig(axis="z", axis_number=25)
    grid.save_fig(axis="z", axis_number=50)
    grid.save_fig(axis="z", axis_number=75)
    grid.plot_n(grid=grid, axis="z", axis_index=25)
    grid.plot_n(grid=grid, axis="z", axis_index=50)
    grid.plot_n(grid=grid, axis="z", axis_index=75)