import utils
from photfdtd import Waveguide, Grid, Solve

if __name__ == "__main__":
    background_index = 1.0

    # 设置器件参数
    waveguide = Waveguide(
        xlength=25, ylength=20, zlength=1, x=40, y=50, z=0, refractive_index=3.47638, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=80, grid_ylength=100, grid_zlength=1, grid_spacing=20e-9,
                permittivity=background_index ** 2,
                foldername="test_eigenmode_solver")

    # 添加波导
    grid.add_object(waveguide)

    # 接下来我们绘制z=0截面的折射率分布，并计算在该截面处的五个模式
    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    # 绘制截面折射率分布
    solve.plot()

    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data = solve.calculate_mode(lam=1550e-9, neff=3.47638, neigs=2,
                                x_boundary_low="pml",
                                y_boundary_low="pml",
                                x_boundary_high="pml",
                                y_boundary_high="pml",
                                x_thickness_low=5,
                                y_thickness_low=15,
                                x_thickness_high=10,
                                y_thickness_high=20,
                                background_index=background_index)

    # 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    solve.draw_mode(filepath=solve.filepath,
                    data=data,
                    content="amplitude")
    # 也可以是场的相位、实部或虚部
    # solve.draw_mode(filepath=solve.filepath,
    #                 data=data,
    #                 content="phase")
    # solve.draw_mode(filepath=solve.filepath,
    #                 data=data,
    #                 content="real_part")
    # solve.draw_mode(filepath=solve.filepath,
    #                 data=data,
    #                 content="imaginary_part")

    # 如果保存了模式的数据，则可以读取它再绘制模式场
    # Solve.save_mode(solve.filepath, data)
    #
    # data_from_saved_modes = Solve.read_mode(solve.filepath)
    #
    # Solve.draw_mode(filepath=solve.filepath, data=data_from_saved_modes, content="real_part")
