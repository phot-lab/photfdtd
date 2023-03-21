import utils
from photfdtd import Ring, Grid

if __name__ == "__main__":

    ring = Ring(
        outer_radius=50,
        zlength=1,
        x=10,
        y=10,
        z=1,
        width=4,
        length=0,
        gap=0,
        name="ring",
        refractive_index=1.7,
        direction=1,
    )

    grid = Grid(grid_xlength=120, grid_ylength=130, grid_zlength=1, grid_spacing=155e-9, total_time=1000, pml_width=5)

    grid.set_source(
        source_type="linesource",
        x=8,
        xlength=0,
        y=ring.y - ring.width - ring.gap - 1,
        ylength=7,
        period=1550e-9 / 299792458,
    )

    grid.add_object(ring)

    grid.savefig("Ring.png", axis="z")
