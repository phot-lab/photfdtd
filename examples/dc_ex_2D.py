import utils
from photfdtd import DirectionalCoupler, Grid, Solve

if __name__ == "__main__":
    background_index = 1.455

    grid = Grid(grid_xlength=8e-6, grid_ylength=1, grid_zlength=12e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_dc_2D")
    dc = DirectionalCoupler(
        xlength_sbend=1.8e-6,
        zlength_sbend=3e-6,
        ylength=1,
        width_1=0.6e-6,
        width_2=0.4e-6,
        name="dc",
        refractive_index=3.47,
        zlength_rectangle=4e-6,
        gap=0.6e-6,
        grid=grid
    )
    #
    # grid.set_source(source_type="linesource", period=1550e-9 / 299792458, x=5.7e-6, y=0, z=0.9e-6, xlength=0.5e-6,
    #                 zlength=1, ylength=1 * 20e-9, polarization="x")

    # grid.set_detector(detector_type='blockdetector',
    #                   x=175, xlength=0,
    #                   y=80, ylength=dc.width + 4,
    #                   z=12, zlength=dc.width + 2,
    #                   name='detector')

    grid.add_object(dc)

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='y',
                  index=0,
                  filepath=grid.folder
                  )

    solve.plot()

    grid.save_fig(axis="y", axis_number=0, geo=solve.geometry)

    grid.run()

    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)


    #
    # # 保存仿真结果
    # grid.save_simulation()

    # # 绘制任意截面场图
    # grid.visualize(x=100, showEnergy=True, show=True, save=True)
    # grid.visualize(z=12, showEnergy=True, show=True, save=True)
    #
    # # 读取仿真结果
    # data = grid.read_simulation(folder=grid.folder)
