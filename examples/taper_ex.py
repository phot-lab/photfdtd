import utils
from photfdtd import Ysplitter, Grid, Solve, constants

if __name__ == "__main__":

    background_index=1.0

    # 设置器件参数
    ysplitter = Ysplitter(xlength=200, ylength=160, zlength=20, x=100, y=100, z=13, direction=1, width=20, name="ysplitter",
                          refractive_index=3.47, xlength_waveguide=80, xlength_taper=40, ylength_taper=40,
                          width_sbend=20, background_index=background_index)

    # 设置 grid 参数
    grid = Grid(grid_ylength=200, grid_xlength=200, grid_zlength=25, grid_spacing=20e-9, total_time=1000,
                pml_width_x=20,
                pml_width_y=20,
                pml_width_z=1,
                foldername="test_ysplitter", permittivity=background_index ** 2)

    # 设置光源
    grid.set_source(source_type="planesource", period=1550e-9 / constants.c, name="source", x=30, y=100, z=13,
                    xlength=1, ylength=22, zlength=22)

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=175,
                      y=63,
                      z=13,
                      xlength=1,
                      ylength=25,
                      zlength=22
                      )

    grid.add_object(ysplitter)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve.plot()

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.visualize(x=100, showEnergy=True, show=True, save=True)
    grid.visualize(z=13, showEnergy=True, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)