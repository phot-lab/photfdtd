import utils
from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":

    # 设置器件参数
    waveguide = Waveguide(
        xlength=20, ylength=200, zlength=1, x=50, y=100, z=0, width=10, refractive_index=3.47, name="Waveguide"
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=100, grid_ylength=200, grid_zlength=1, grid_spacing=50e-9, total_time=1,
                foldername="test_waveguide")

    # 往 grid 里添加一个器件
    grid.add_object(waveguide)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制截面
    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    grid.save_fig(axis="z",
                  axis_number=0)

