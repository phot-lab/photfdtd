import utils
from photfdtd import Ring, Grid, Solve

if __name__ == "__main__":

    background_index = 1.0

    ring = Ring(
        outer_radius=100,
        zlength=1,
        x=150,
        y=150,
        z=0,
        width=20,
        length=0,
        gap=5,
        name="ring",
        refractive_index=3.47,
        direction=1,
        background_index=background_index
    )

    grid = Grid(grid_xlength=300, grid_ylength=300, grid_zlength=1, grid_spacing=20e-9, total_time=1000,
                pml_width_x=10, pml_width_y=10, pml_width_z=0,
                permittivity=background_index ** 2, foldername="test_ring")

    grid.set_source(
        source_type="linesource",
        x=100,
        xlength=0,
        y=ring.y - ring.width - ring.gap - 1,
        ylength=21,
        pulse_type="None",
        z=0,
        zlength=0,
        period=1550e-9 / 299792458,
    )

    grid.set_detector(detector_type="linedetector",
                      x=250,
                      xlength=0,
                      y=ring.y - ring.width - ring.gap - 1,
                      ylength=21,
                      z=0,
                      zlength=0,
                      name="linedetector")

    grid.add_object(ring)

    # 创建solve对象
    solve = Solve(grid=grid)

    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    grid.save_simulation()

    grid.save_fig(axis="z",
                  axis_number=0)

    data = Grid.read_simulation(folder=grid.folder)
