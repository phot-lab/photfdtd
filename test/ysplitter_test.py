import utils
from photfdtd import Ysplitter

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
    ysplitter.set_grid(
        grid_ylength=80, grid_xlength=80, grid_zlength=1, grid_spacing=155e-9, total_time=200, pml_width=5
    )

    # 设置光源
    ysplitter.set_source()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    ysplitter.savefig(filepath="YSplitterZ.png", axis="z")
