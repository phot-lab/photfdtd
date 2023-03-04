import utils
from photfdtd import Waveguide, Grid

if __name__ == "__main__":

    # 设置器件参数
    waveguide = Waveguide(
        xlength=40, ylength=20, zlength=10, x=20, y=40, z=5, width=10, refractive_index=1.7, name="Waveguide"
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=0.01, total_time=1, pml_width=10)

    # 往 grid 里添加一个器件
    grid.add_object(waveguide)

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图（这里画了三张图）
    grid.savefig(filepath="WaveguideX.png", axis="x")
    grid.savefig(filepath="WaveguideY.png", axis="y")
    grid.savefig(filepath="WaveguideZ.png", axis="z")
