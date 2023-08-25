import utils
from photfdtd import Mmi, Grid, Solve

if __name__ == "__main__":
    n = 1 # 输入端口数
    m = 2  # 输出端口数
    grid_spacing = 50e-9  # 空间步长

    background_index = 1.0

    mmi = Mmi(
        xlength=1770,
        ylength=560,
        zlength=1,
        We=560,
        x=2500,
        y=1000,
        z=0,
        name="mmi",
        refractive_index=3.47,
        n=n,
        m=m,
        width_port=100,
        width_wg=80,
        l_port=500,
        ln=500,
        lm=500,
        background_index=background_index
    )

    grid = Grid(grid_xlength=5000, grid_ylength=2000, grid_zlength=1, grid_spacing=grid_spacing, total_time=1,
                pml_width_x=20,
                pml_width_y=5, pml_width_z=0, foldername="test_mmi",
                permittivity=background_index ** 2)

    # for i in range(mmi.n):
    #     grid.set_source(
    #         x=9,
    #         xlength=0,
    #         y=mmi.ports_in[i].y,
    #         ylength=mmi.ports_in[i].ylength,
    #         source_type="linesource",
    #         period=1550e-9 / 299792458,
    #     )

    grid.set_source(
        x=75, xlength=0, y=mmi.y - 15, ylength=30, z=0, zlength=0, source_type="linesource",
        period=1550e-9 / 299792458,
        pulse_type="None",
        cycle=5,
        pulse_length=40e-15,
        offset=41e-15
    )

    grid.add_object(mmi)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制x=50截面
    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    grid.save_fig(axis="z",
                  axis_number=0)

