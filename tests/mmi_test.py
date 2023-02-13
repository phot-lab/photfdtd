import utils
from photfdtd import Mmi

if __name__ == "__main__":
    n = 1  # 输入端口数
    m = 2  # 输出端口数
    grid_spacing = 110e-9  # 空间步长

    mmi = Mmi(
        xlength=118,
        ylength=36,
        zlength=1,
        We=37,
        x=50,
        y=10,
        z=1,
        direction=1,
        name="mmi",
        refractive_index=3.47,
        n=n,
        m=m,
        width_port=8,
        width_wg=2,
        l_port=10,
        ln=40,
        lm=5,
    )

    mmi.set_box()
    mmi.set_ports()
    mmi.set_grid(pml_width=5, total_time=1500, grid_spacing=110e-9, permittivity=1)

    mmi.savefig("Mmi.png", axis="z")
