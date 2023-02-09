import utils
from photfdtd import Sbend


if __name__ == "__main__":

    # 设置器件参数
    sbend = Sbend(
        xlength=40, ylength=60, zlength=1, x=10, y=10, z=1, direction=-1, width=10, refractive_index=1.7, name="sbend"
    )

    # 设置 grid 参数
    sbend.set_grid(grid_xlength=80, grid_ylength=80, grid_zlength=1, grid_spacing=155e-9, total_time=200, pml_width=10)

    # 设置光源
    sbend.set_source()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    sbend.savefig(filepath="SbendZ.png", axis="z")
