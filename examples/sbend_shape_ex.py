import utils
from photfdtd import SbendShape, Grid


if __name__ == "__main__":
    # 设置器件参数
    sbend = SbendShape(
        xlength=70, ylength=70, zlength=1, x=10, y=10, z=1, direction=-1, width=10, refractive_index=1.7, name="sbend"
    )

    # 设置 grid 参数
    grid = Grid(grid_xlength=100, grid_ylength=100, grid_zlength=1, grid_spacing=155e-9, total_time=1000, pml_width=10)

    # 设置光源
    grid.set_source(
        source_type="linesource", x=11 + sbend.xlength, xlength=0, y=sbend.y, ylength=10, period=1550e-9 / 299792458
    )

    # 添加器件
    grid.add_object(sbend)

    # Run a FDTD simulation
    grid.run()

    # 保存图片
    grid.savefig(filepath="SbendShapeZ_60x60.png", z=0)
