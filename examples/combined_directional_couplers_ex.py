import utils
from photfdtd import Grid, DirectionalCoupler

if __name__ == "__main__":
    dc1 = DirectionalCoupler(
        xlength=125,
        ylength=65,
        zlength=1,
        x=10,
        y=10,
        z=1,
        direction=1,
        width=4,
        name="dc1",
        refractive_index=1.7,
        xlength_rectangle=35,
        gap=1,
    )

    dc2 = DirectionalCoupler(
        xlength=125,
        ylength=65,
        zlength=1,
        x=dc1.x + 125,
        y=dc1.y + 61,
        z=1,
        direction=1,
        width=4,
        name="dc2",
        refractive_index=1.7,
        xlength_rectangle=35,
        gap=1,
    )

    grid = Grid(grid_xlength=280, grid_ylength=150, grid_zlength=1, grid_spacing=155e-9, total_time=800, pml_width=9)

    grid.add_object(dc1)
    grid.add_object(dc2)

    grid.set_source(
        x=dc1.x,
        xlength=0,
        y=dc1.y,
        ylength=dc1.width,
        source_type="linesource",
        period=1550e-9 / 299792458,
        pulse=False,
    )

    grid.run()

    grid.savefig(filepath="CombinedDirectionalCouplers.png", z=0)
