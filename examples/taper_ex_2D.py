import utils
from photfdtd import Ysplitter, Grid, Solve, Taper

if __name__ == "__main__":
    background_index = 1.4447

    # 设置 grid 参数
    grid = Grid(grid_xlength=4e-6, grid_ylength=1, grid_zlength=8e-6, grid_spacing=20e-9,
                foldername="test_taper_2D", permittivity=background_index ** 2)

    # 设置器件参数
    taper = Taper(xlength=2000e-9, width=1000e-9, ylength=1, zlength=6000e-9, name="taper", refractive_index=3.47,
                  grid=grid)

    grid.add_object(taper)
    grid.save_fig(axis="y", axis_number=0)
    grid.plot_n(axis="y", axis_index=0)

    grid.set_source(source_type="linesource", wavelength=1550e-9, name="source", x=2e-6, y=0, z=1e-6,
                    xlength=30, ylength=1, zlength=1, polarization="x")
    grid.set_detector(detector_type='linedetector',
                      x_start=1e-6, y_start=0e-6, z_start=7e-6,
                      x_end=3e-6, y_end=0e-6, z_end=7e-6,
                      name='detector1')

    # run the FDTD simulation 运行仿真
    grid.run()
    grid.save_simulation()

    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    grid.save_fig(axis="y", axis_number=0, show_energy=True)

    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(folder=grid.folder, data=data, field="E", field_axis="x",
                        index=5, name_det="detector1")