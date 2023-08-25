import utils
from photfdtd import DirectionalCoupler, Grid, Solve

if __name__ == "__main__":

    background_index = 1.455

    dc = DirectionalCoupler(
        xlength=125,
        ylength=65,
        zlength=1,
        x=100,
        y=100,
        z=0,
        direction=1,
        width=4,
        name="dc",
        refractive_index=3.47,
        xlength_rectangle=35,
        gap=1,
        background_index=background_index
    )

    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=50e-9, total_time=1000,
                pml_width_x=20,
                pml_width_y=20, pml_width_z=0,
                permittivity=background_index ** 2, foldername="test_dc")

    grid.set_source(
        x=dc.x, xlength=0, y=dc.y, ylength=dc.width, source_type="linesource", period=1550e-9 / 299792458, pulse=False
    )

    grid.set_detector(detector_type='linedetector',
                      x=dc.x, xlength=0, y=dc.y + dc.ylength - dc.width, ylength=dc.width, z=0, zlength=0,
                      name='detector_source')

    grid.add_object(dc)

    # 创建solve对象
    solve = Solve(grid=grid)

    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    grid.save_fig(axis="z",
                  axis_number=0,
                  )