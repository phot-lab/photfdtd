import photfdtd.fdtd.constants as constants
from photfdtd import Sbend, Grid, Solve, Waveguide,fdtd
fdtd.set_backend("numpy")

if __name__ == "__main__":
    background_index = 1.4447

    # 设置 grid 参数
    grid = Grid(grid_xlength=200 * 20e-9, grid_ylength=1, grid_zlength=8000e-9, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_sbend_2D")

    # 设置波导参数
    sbend = Sbend(
        xlength=100 * 20e-9,
        ylength=1,
        zlength=150 * 20e-9,
        x=2e-6,
        z=3e-6,
        direction=1,
        width=20 * 20e-9,
        refractive_index=3.45,
        name="sbend",
        grid=grid,
    )

    waveguide = Waveguide(
        xlength=0.4e-6, ylength=1, zlength=1.5e-6, x=2.8e-6, y=0, z=5.25e-6, refractive_index=3.45, name="Waveguide", grid=grid
    )

    # 添加器件
    grid.add_object(sbend)
    grid.save_fig(axis="y", axis_index=0)
    grid.plot_n(axis="y", axis_index=0)


    grid.add_object(waveguide)

    grid.plot_field(field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source",x=1.2e-6, y=0, z=1.4e-6,
                    xlength=500e-9, ylength=1, zlength=1, polarization="x")

    grid.save_fig(axis="y", axis_number=0)

    # 设置监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector",
                      x=2.8e-6,
                      y=0,
                      z=4.5e-6,
                      xlength=0.4e-6,
                      ylength=1,
                      zlength=1
                      )

    # 运行仿真
    grid.run(save=True)
    grid.visualize()

