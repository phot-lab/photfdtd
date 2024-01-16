import utils
from photfdtd import Ring, Grid, Solve

if __name__ == "__main__":
    background_index = 1.0

    grid = Grid(grid_xlength=300, grid_ylength=300, grid_zlength=1, grid_spacing=20e-9, total_time=1,
                pml_width_x=50, pml_width_y=20, pml_width_z=0,
                permittivity=background_index ** 2, foldername="test_ring")

    ring = Ring(
        outer_radius=100 * 20e-9,
        zlength=1 * 20e-9,
        width=10 * 20e-9,
        length=0 * 20e-9,
        gap=5 * 20e-9,
        name="ring",
        refractive_index=3.47,
        direction=1,
        grid=grid
    )

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, pulse_type="None", x=100, y=35, z=0,
                    xlength=0, ylength=21, zlength=1)

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
                  axis='z',
                  index=0,
                  filepath=grid.folder)

    solve.plot()

    grid.run()

    grid.save_fig(axis="z",
                  axis_number=0)
    # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="z", axis="z", axis_index=0, folder=grid.folder)
