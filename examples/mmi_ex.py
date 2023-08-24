import utils
from photfdtd import Mmi, Grid

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

    grid_xlength = mmi.xlength + mmi.ln + mmi.lm + mmi.l_port * 2
    grid_ylength = mmi.ylength + 2 * 5 + 10
    grid_zlength = 1
    grid = Grid(
        pml_width_x=5,
        pml_width_y=5,
        pml_width_z=5,
        total_time=1500,
        grid_spacing=110e-9,
        grid_xlength=grid_xlength,
        grid_ylength=grid_ylength,
        grid_zlength=grid_zlength,
    )

    for i in range(mmi.n):
        grid.set_source(
            x=9,
            xlength=0,
            y=mmi.ports_in[i].y,
            ylength=mmi.ports_in[i].ylength,
            source_type="linesource",
            period=1550e-9 / 299792458,
        )

    grid.add_object(mmi)

    grid.run()

    grid.savefig("Mmi.png", z=0)
