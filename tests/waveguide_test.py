import utils
from photfdtd import Waveguide

if __name__ == "__main__":

    # 设置器件参数
    waveguide = Waveguide(
        xlength=40, ylength=20, zlength=10, x=20, y=40, z=5, width=10, refractive_index=1.7, name="Waveguide"
    )

    # 设置 grid 参数
    waveguide.set_grid(
        grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=0.01, total_time=1, pml_width=10
    )

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图（这里画了三张图）
    waveguide.savefig(filepath="WaveguideX.png", axis="x")
    waveguide.savefig(filepath="WaveguideY.png", axis="y")
    waveguide.savefig(filepath="WaveguideZ.png", axis="z")
