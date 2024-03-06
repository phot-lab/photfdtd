import utils
from photfdtd import Ring, Grid, Solve

if __name__ == "__main__":
    background_index = 1.4447

    grid = Grid(grid_xlength=350, grid_ylength=1, grid_zlength=350, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_ring_2D")

    ring = Ring(outer_radius=100 * 20e-9, ylength=1 * 20e-9, width_s=10 * 40e-9,length=50 * 20e-9, gap=5 * 20e-9,
                name="ring", refractive_index=3.47, direction=1, grid=grid)

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, pulse_type="None", x=1.3e-6, y=0, z=1e-6,
                    xlength=21, ylength=1, zlength=1, polarization="x")
    # grid.set_source(source_type="pointsource", period=1550e-9 / 299792458, pulse_type="None", x=1.3e-6, y=1.3e-6, z=0,
    #                 polarization="y")

    # grid.set_detector(detector_type="blockdetector",
    #                   x=250,
    #                   xlength=0,
    #                   y=37,
    #                   ylength=21,
    #                   z=13,
    #                   zlength=22,
    #                   name="detector")

    grid.add_object(ring)

    # 创建solve对象
    solve = Solve(grid=grid,
                  axis='y',
                  index=0,
                  filepath=grid.folder)

    solve.plot()

    grid.run()

    grid.save_fig(axis="y", axis_number=0)
    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder,
                    vmax=2)
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
