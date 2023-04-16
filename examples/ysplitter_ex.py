import utils
from photfdtd import Ysplitter, Grid

if __name__ == "__main__":

    # 设置器件参数
    ysplitter = Ysplitter(
        xlength=60,
        ylength=60,
        zlength=1,
        x=10,
        y=10,
        z=1,
        direction=-1,
        width=10,
        name="ysplitter",
        refractive_index=1.7,
        xlength_rectangle=20,
        xlength_trapezoid=10,
        ylength_trapezoid=20,
    )

    # 设置 grid 参数
    grid = Grid(grid_ylength=80, grid_xlength=80, grid_zlength=1, grid_spacing=155e-9, total_time=200, pml_width=5)

    # 设置光源
    grid.set_source(x=60, xlength=0, y=35, ylength=10, source_type="linesource", period=1550e-9 / 299792458)

    grid.add_object(ysplitter)

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    grid.savefig(filepath="YSplitterZ.png", z=0)
