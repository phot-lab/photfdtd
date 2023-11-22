import utils
from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":

    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=40, ylength=40, zlength=1, x=75, y=75, z=0, refractive_index=3.47638, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=150, grid_ylength=150, grid_zlength=1, grid_spacing=10e-9, total_time=1,
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
    solve.plot(axis='z',
               index=0,
               filepath=grid.folder)

    # 计算这个截面处，波长1.55um，折射率3.47附近的10个模式，并绘制
    solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2, component="Ex")
    solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2, component="Ey")
    solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2, component="Ez")
    solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2, component="Hx")
    solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2, component="Hy")
    solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2, component="Hz")

    # 打印这些模式对应的有效折射率
    print(solve.effective_index)

