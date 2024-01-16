from photfdtd import Waveguide, Arc, Grid, Solve, constants

if __name__ == "__main__":

    background_index=1.0

    # 设置器件参数
    waveguide1 = Waveguide(
        xlength=100, ylength=20, zlength=20, x=50, y=149, z=11, refractive_index=3.47, name="Waveguide1",
        background_index=background_index
    )
    arc = Arc(outer_radius=60, zlength=20, x=100, y=100, z=1, width=20, refractive_index=3.47, name="arc", direction=2,
              background_index=background_index)
    waveguide2 = Waveguide(
        xlength=20, ylength=100, zlength=20, x=149, y=50, z=11, refractive_index=3.47, name="Waveguide2",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=22, grid_spacing=20e-9, total_time=1000,
                foldername="test_arc",
                pml_width_x=25,
                pml_width_y=25,
                pml_width_z=0,
                permittivity=background_index ** 2,)

    # 往 grid 里添加器件
    grid.add_object(arc)
    grid.add_object(waveguide2)
    grid.add_object(waveguide1)

    # 设置光源
    grid.set_source(source_type="planesource", period=1550e-9 / constants.c, name="source", x=30, y=150, z=11,
                    xlength=1, ylength=waveguide1.ylength + 4, zlength=waveguide1.zlength)

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      x=150,
                      y=30,
                      z=11,
                      xlength=waveguide2.xlength + 4,
                      ylength=1,
                      zlength=waveguide1.zlength
                      )

    solve = Solve(grid=grid)

    # 绘制任一截面
    solve.plot()

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.visualize(y=150, showEnergy=True, show=True, save=True)
    grid.visualize(z=11, showEnergy=True, show=True, save=True)
    grid.visualize(x=150, showEnergy=True, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)