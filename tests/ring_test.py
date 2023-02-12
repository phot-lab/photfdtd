import utils
from photfdtd import Ring

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

    ring.set_grid(
        grid_xlength=120, grid_ylength=130, grid_zlength=1, grid_spacing=155e-9, total_time=1000, pml_width=5
    )

    ring.savefig("Ring.png", axis="z")
