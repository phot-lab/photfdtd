import utils
from photfdtd import Ring, Grid

if __name__ == "__main__":

    ring = Ring(
        outer_radius=40,
        zlength=1,
        x=20,
        y=20,
        z=1,
        width=4,
        length=0,
        gap=1,
        name="ring",
        refractive_index=3.47,
        direction=1,
    )

    ring1 = Ring(
        outer_radius=40,
        zlength=1,
        x=100,
        y=100,
        z=1,
        width=4,
        length=0,
        gap=1,
        name="ring1",
        refractive_index=3.47,
        direction=1,
    )

    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=155e-9, total_time=1500, pml_width=5)

    grid.set_source(
        source_type="linesource",
        x=16,
        xlength=0,
        y=ring.y - ring.width - ring.gap - 1,
        ylength=7,
        period=1550e-9 / 299792458,
    )

    grid.add_object(ring)
    grid.add_object(ring1)

    grid.run()

    grid.savefig("CombinedRings.png", z=0)
