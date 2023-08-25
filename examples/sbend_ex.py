import utils
from photfdtd import Sbend, Grid, Solve


if __name__ == "__main__":

    background_index=1.0

    # 设置波导参数
    sbend = Sbend(
        xlength=600, ylength=390, zlength=1, x=400, y=400, z=0, direction=-1, width=100, refractive_index=1.7, name="sbend",
        background_index=background_index
    )

    # 设置 grid 参数
    grid = Grid(grid_xlength=800, grid_ylength=800, grid_zlength=1, grid_spacing=155e-9,
                total_time=1, foldername="test_sbend", permittivity=background_index ** 2)

    # 设置光源
    # grid.set_source(
    #     source_type="linesource", x=11 + sbend.xlength, xlength=0, y=sbend.y, ylength=10, period=1550e-9 / 299792458
    # )

    # 添加器件
    grid.add_object(sbend)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制截面
    solve._plot_(axis='z',
                 index=-1,
                 filepath=grid.folder)

    grid.run()

    # 保存图片
    grid.save_fig(axis_number=0, axis="z")
