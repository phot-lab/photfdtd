import utils
from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":
    # 设置波导参数
    waveguide = Waveguide(
        xlength=1, ylength=50, zlength=50, x=0, y=50, z=50, width=10, refractive_index=3.47638, name="Waveguide"
    )
    # substrate = Waveguide(
    #     xlength=1, ylength=100, zlength=12, x=0, y=0, z=0, width=10, refractive_index=1.44, name="substrate"
    # )
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=1, grid_ylength=100, grid_zlength=100, grid_spacing=10e-9, total_time=1,
                pml_width_x=10, pml_width_y=1, pml_width_z=0, foldername="test_solve",
                permittivity=1.44 ** 2)

    # 往 grid 里添加一个器件
    grid.add_object(waveguide)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制截面折射率分布
    solve._plot_(axis='x',
                 index=0,
                 filepath=grid.folder)

    # 计算这个截面处，波长1.55um，折射率3.47附近的10个模式
    solve._calculate_mode(lam=1.55, neff=3.47, neigs=10)

    # 绘制计算的10个模式并保存，绘制时使用6个等高线
    solve._draw_mode(neigs=10)

    # 计算各个模式的TEfraction，并保存图片
    # solve._calculate_TEfraction(n_levels=6)

    print(solve.effective_index)

    #频率扫描，波长范围为[1.45um, 1.55um] 一共计算五个点
    # solve._sweep_(steps=5,
    #               lams=[1.45, 1.55])
