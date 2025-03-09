import utils
from photfdtd import FWG, Waveguide, Grid, Solve
from numpy import pi

if __name__ == "__main__":
    background_index = 1.4447
    n_Si = 3.476

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=1, grid_zlength=200, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_fwg_2D")

    # 设置器件参数
    fwg = FWG(outer_radius=2e-6, ylength=1 * 20e-9, refractive_index=n_Si, name="fwg",
              z=0.8e-6,
              grid=grid, angle_psi=pi / 3, angle_phi=pi / 3, period=10 * 20e-9, duty_cycle=0.4, number=10)

    # 往 grid 里添加器件
    grid.add_object(fwg)
    grid.save_fig(axis="y", axis_number=0)
    grid.plot_n(grid=grid, axis="y", axis_index=0)

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458, x=2e-6, y=0, z=3e-6, xlength=10, polarization="x")
    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, y_start=0e-6, z_start=0.8e-6,
                      x_end=2.2e-6, y_end=0e-6, z_end=0.8e-6,
                      name='detector1')
    grid.run()
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 保存仿真结果
    grid.save_simulation()
    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    # # 读取仿真结果
    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")