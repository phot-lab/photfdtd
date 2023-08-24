import utils
from photfdtd import DirectionalCoupler, Grid

if __name__ == "__main__":
    dc = DirectionalCoupler(
        xlength=150,
        ylength=65,
        zlength=1,
        x=20,
        y=20,
        z=20,
        direction=1,
        width=4,
        name="dc",
        refractive_index=3.47,
        xlength_rectangle=60,
        gap=1,
    )

    grid = Grid(grid_xlength=175, grid_ylength=120, grid_zlength=1, grid_spacing=155e-9, total_time=1000, pml_width_x=5, pml_width_y=5, pml_width_z=5)

    grid.set_source(
        x=10, xlength=0, y=dc.y, ylength=dc.width, source_type="linesource", period=1550e-9 / 299792458, pulse=True
    )

    grid.add_object(dc)

    grid.run()

    grid.savefig("DirectionalCoupler.png", z=0)
