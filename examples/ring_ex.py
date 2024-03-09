import utils
from photfdtd import Ring, Grid, Solve

if __name__ == "__main__":

    background_index = 1.0

    ring = Ring(outer_radius=100, x=150, y=150, z=13, width_s=20, length=0, gap=5, name="ring", refractive_index=3.47,
                direction=1)

    grid = Grid(grid_xlength=300, grid_ylength=300, grid_zlength=25, grid_spacing=20e-9, total_time=1000,
                pml_width_x=50, pml_width_y=20, pml_width_z=1,
                permittivity=background_index ** 2, foldername="test_ring")

    grid.set_source(
        source_type="planesource",
        x=100,
        xlength=0,
        y=35,
        ylength=21,
        pulse_type="None",
        z=13,
        zlength=22,
        period=1550e-9 / 299792458,
    )

    grid.set_detector(detector_type="blockdetector",
                      x=250,
                      xlength=0,
                      y=37,
                      ylength=21,
                      z=13,
                      zlength=22,
                      name="detector")

    grid.add_object(ring)

    # 创建solve对象
    solve = Solve(grid=grid)

    solve.plot()

    grid.run()

    grid.save_simulation()

    grid.visualize(x=150, showEnergy=True, show=True, save=True)
    grid.visualize(z=13, showEnergy=True, show=True, save=True)

    data = Grid.read_simulation(folder=grid.folder)
