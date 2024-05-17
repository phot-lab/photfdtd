import utils
from photfdtd import TFF, Grid, Solve

if __name__ == "__main__":
    grid_spacing = 20e-9  # 空间步长

    background_index = 1.0

    grid = Grid(grid_xlength=6e-6, grid_ylength=1, grid_zlength=6e-6, grid_spacing=grid_spacing,
                foldername="test_tff",
                permittivity=background_index ** 2)

    # 制作一个11层厚，1550nm波长的增返膜
    tff = TFF(
        xlength=250 * grid_spacing,
        ylength=1,
        x=150,
        y=0,
        z=0.8e-6,
        name="TFF",
        layers=11,
        axis="z",
        low_index=1.35,
        high_index=2.35,
        dh=8 * grid_spacing,
        dl=14 * grid_spacing,
        grid=grid
    )

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, name="source", x=150, y=0, z=220, xlength=50,
                    ylength=0, zlength=0, polarization="x")
    grid.set_detector(detector_type='linedetector',
                      x_start=2.7e-6, y_start=0e-6, z_start=5e-6,
                      x_end=3.2e-6, y_end=0e-6, z_end=5e-6,
                      name='detector1')

    grid.add_object(tff)
    grid.plot_n(grid=grid, axis="y", axis_index=0)
    grid.save_fig(axis="y", axis_number=0)

    # 运行仿真
    grid.run()
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 保存仿真结果
    grid.save_simulation()
    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0)
    # # 读取仿真结果
    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")