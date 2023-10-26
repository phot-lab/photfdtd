import utils
from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":

    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=200, ylength=20, zlength=20, x=100, y=30, z=30, refractive_index=3.47, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=60, grid_zlength=60, grid_spacing=20e-9, total_time=800,
                pml_width_x=10,
                pml_width_y=1,
                pml_width_z=1,
                permittivity=background_index ** 2,
                foldername="test_eigenmode_solver")

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制截面折射率分布
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率3.47附近的10个模式
    solve.calculate_mode(lam=1.55, neff=3.47, neigs=10)

    # 绘制计算的10个模式并保存
    solve.draw_mode(neigs=10, component="ex")

    # 计算各个模式的TEfraction，并保存图片
    # solve._calculate_TEfraction(n_levels=6)
    # 打印这些模式对应的有效折射率
    print(solve.effective_index)

    #频率扫描，波长范围为[1.45um, 1.55um] 一共计算五个点
    # solve._sweep_(steps=5,
    #               lams=[1.45, 1.55])
