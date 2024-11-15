import utils
from photfdtd import Ring, Grid

if __name__ == "__main__":

    ring = Ring(outer_radius=40, x=20, y=20, z=1, width_s=4, length=0, gap=1, name="ring", refractive_index=3.47,
                direction=1)

    ring1 = Ring(outer_radius=40, x=100, y=100, z=1, width_s=4, length=0, gap=1, name="ring1", refractive_index=3.47,
                 direction=1)

    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=155e-9, total_time=1500, pml_width_x=5, pml_width_y=5, pml_width_z=5)

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, x=16, y=ring.y - ring.width - ring.gap - 1,
                    xlength=0, ylength=7)

    grid.add_object(ring)
    grid.add_object(ring1)

    grid.run()

    grid.savefig("CombinedRings.png", z=0)
