import utils
from photfdtd import DirectionalCoupler

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

    dc.set_grid(
        grid_xlength=175,
        grid_ylength=120,
        grid_zlength=1,
        grid_spacing=155e-9,
        total_time=1000,
        pml_width=5,
        permittivity=1**2,
    )

    dc.savefig("DirectionalCoupler.png", axis="z")
