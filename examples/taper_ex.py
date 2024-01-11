import utils
from photfdtd import Ysplitter, Grid, Solve, constants, Taper

if __name__ == "__main__":
    background_index = 1.4447

    taper = Taper(xlength=100,
                  ylength=25,
                  zlength=10,
                  x=100,
                  y=30,
                  z=25,
                  direction=1,
                  width=7,
                  name="taper",
                  refractive_index=3.47,
                  background_index=background_index)

    # 设置 grid 参数
    grid = Grid(grid_ylength=60, grid_xlength=200, grid_zlength=50, grid_spacing=20e-9, total_time=1,
                pml_width_x=20,
                pml_width_y=20,
                pml_width_z=10,
                foldername="test_taper", permittivity=background_index ** 2)

    # grid.set_source(source_type="planesource", period=1550e-9 / constants.c, name="source", x=30, y=100, z=13,
    #                 xlength=1, ylength=22, zlength=22)

    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=175,
    #                   y=63,
    #                   z=13,
    #                   xlength=1,
    #                   ylength=25,
    #                   zlength=22
    #                   )

    grid.add_object(taper)

    # 创建solve对象
    solve_fiber_side = Solve(grid=grid,
                             axis='x',
                             index=50,
                             filepath=grid.folder)

    solve_wg_side = Solve(grid=grid,
                          axis='x',
                          index=148,
                          filepath=grid.folder)

    # 绘制任一截面折射率分布
    solve_fiber_side.plot()
    solve_wg_side.plot()

    # 计算这个截面处，波长1.55um，折射率3.47附近的2个模式，边界条件选择在四个方向上都是pml，厚度均为15格
    data_fiber_side = solve_fiber_side.calculate_mode(lam=1550e-9, neff=2, neigs=5,
                                                      x_boundary_low="pml", y_boundary_low="pml",
                                                      x_boundary_high="pml",
                                                      y_boundary_high="pml",
                                                      x_thickness_low=15,
                                                      y_thickness_low=10, x_thickness_high=15,
                                                      y_thickness_high=10,
                                                      background_index=background_index)

    data_wg_side = solve_wg_side.calculate_mode(lam=1550e-9, neff=3.47, neigs=2,
                                                   x_boundary_low="pml", y_boundary_low="pml",
                                                   x_boundary_high="pml",
                                                   y_boundary_high="pml",
                                                   x_thickness_low=15,
                                                   y_thickness_low=10, x_thickness_high=15,
                                                   y_thickness_high=10,
                                                   background_index=background_index)

    # 接下来即可绘制模式场，我们选择绘制amplitude，即幅值。filepath为保存绘制的图片的路径
    Solve.draw_mode(filepath=solve_fiber_side.filepath,
                    data=data_fiber_side,
                    content="amplitude")

    # Solve.draw_mode(filepath=solve_wg_side.filepath,
    #                 data=data_wg_side,
    #                 content="amplitude")
    # 运行仿真
    grid.run()


    grid.save_fig(axis="z",
                  axis_number=25)
