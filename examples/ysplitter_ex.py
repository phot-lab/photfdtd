import utils
from photfdtd import Ysplitter, Grid, Solve

if __name__ == "__main__":

    background_index=1.0

    # 设置器件参数
    ysplitter = Ysplitter(xlength=600, ylength=600, zlength=1, x=500, y=500, z=0, direction=1, width=100, name="ysplitter",
                          refractive_index=1.7, xlength_waveguide=200, xlength_taper=100, ylength_taper=200,
                          width_sbend=100, background_index=background_index)

    # 设置 grid 参数
    grid = Grid(grid_ylength=1000, grid_xlength=1000, grid_zlength=1, grid_spacing=155e-9, total_time=1,
                foldername="test_ysplitter", permittivity=background_index ** 2)

    # 设置光源
    grid.set_source(x=60, xlength=0, y=35, ylength=10, source_type="linesource", period=1550e-9 / 299792458)


    grid.add_object(ysplitter)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制x=50截面
    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    grid.save_fig(axis="z", axis_number=0)
