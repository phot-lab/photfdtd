import utils
from photfdtd import DirectionalCoupler, Grid, Solve

if __name__ == "__main__":
    background_index = 1.455

    grid = Grid(grid_xlength=200 * 20e-9, grid_ylength=100 * 20e-9, grid_zlength=1, grid_spacing=20e-9, total_time=1000,
                pml_width_x=20,
                pml_width_y=8, pml_width_z=0,
                permittivity=background_index ** 2, foldername="test_dc")
    dc = DirectionalCoupler(
        xlength=200 * 20e-9,
        ylength=80 * 20e-9,
        zlength=1,
        direction=1,
        width=20 * 20e-9,
        name="dc",
        refractive_index=3.47,
        xlength_rectangle=50,
        gap=10,
        grid=grid
    )

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, x=25, y=80, z=0, xlength=0,
                    ylength=dc.width + 4, zlength=1 * 20e-9)

    # grid.set_detector(detector_type='blockdetector',
    #                   x=175, xlength=0,
    #                   y=80, ylength=dc.width + 4,
    #                   z=12, zlength=dc.width + 2,
    #                   name='detector')

    grid.add_object(dc)

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )

    solve.plot()

    grid.run()

    grid.save_fig(axis="z",
                  axis_number=0,
                  geo=solve.geometry)
    #
    # # 保存仿真结果
    # grid.save_simulation()

    # # 绘制任意截面场图
    # grid.visualize(x=100, showEnergy=True, show=True, save=True)
    # grid.visualize(z=12, showEnergy=True, show=True, save=True)
    #
    # # 读取仿真结果
    # data = grid.read_simulation(folder=grid.folder)
