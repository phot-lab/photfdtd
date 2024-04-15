import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
    # This file has been used for an example of dBmap and blockdetector.
    background_index = 1.4447
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=4e-6, grid_ylength=1, grid_zlength=8e-6,
                grid_spacing=20e-9,
                permittivity=background_index ** 2,
                foldername="test_waveguide_2D")
    # 设置器件参数
    waveguide = Waveguide(
        xlength=0.5e-6, ylength=1, zlength=6e-6, refractive_index=3.47, name="Waveguide", grid=grid, priority=1
    )

    # 往 grid 里添加器件
    grid.add_object(waveguide)

    # 设置光源
    grid.set_source(source_type="linesource", wavelength=1550e-9, name="source",
                    x=2e-6, y=0, z=0.9e-6, xlength=0.4e-6,
                    ylength=0, zlength=0, polarization="x",pulse_type="gaussian", waveform="gaussian")

    # 设置监视器
    grid.set_detector(detector_type="blockdetector",
                      name="detector",
                      axis="y",
                      xlength=1e-6,
                      zlength=3e-6)
    grid.save_fig(axis="y", axis_number=0)
    grid.plot_n(axis="y", axis_index=0)
    # 运行仿真
    grid.run()

    # 保存仿真结果，并传给data
    data = grid.save_simulation()

    # 如果设置了监视器，绘制监视器范围内光场分布
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    Grid.plot_fieldtime(folder=grid.folder, data=data, field_axis="x", index_3d=[25, 0, 0], name_det="detector")
    Grid.dB_map(folder=grid.folder, total_time=grid._grid.time_passed, data=data, axis="y",
                field="E", name_det="detector", interpolation="spline16", save=True, field_axis="x")

