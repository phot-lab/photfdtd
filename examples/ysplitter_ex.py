import utils
from photfdtd import Ysplitter, Grid, Solve, constants

if __name__ == "__main__":
    # 背景空间折射率
    background_index = 1.4555

    # 设置仿真空间
    grid = Grid(grid_xlength=3e-6, grid_ylength=1.5e-6, grid_zlength=3.5e-6, grid_spacing=20e-9,
                foldername="test_ysplitter", permittivity=background_index ** 2)

    # 设置Y分支波导的各个参数
    ysplitter = Ysplitter(direction=1, width=0.2e-6,
                          name="ysplitter",x=1.5e-6, y=0.75e-6, z=1.5e-6,
                          ylength=0.2e-6,
                          refractive_index=3.45, zlength_waveguide=0.8e-6, xlength_taper=0.4e-6,
                          zlength_taper=0.4e-6,
                          zlength_sbend=1.25e-6,
                          xlength_sbend=1e-6,
                          width_sbend=0.2e-6, grid=grid)

    # 设置光源
    grid.set_source(source_type="linesource", wavelength=850e-9,
                    x_start=1.35e-6, y_start=0.75e-6, z_start=0.5e-6,
                    x_end=1.65e-6, y_end=0.75e-6, z_end=0.5e-6,
                    polarization="x")
    # 设置监视器
    grid.set_detector(detector_type='linedetector',
                      x_start=0.6e-6, y_start=0.75e-6, z_start=2.9e-6,
                      x_end=0.8e-6, y_end=0.75e-6, z_end=2.9e-6,
                      name='detector1')

    # 绘制结构与折射率分布图
    grid.add_object(ysplitter)
    grid.save_fig(axis="y", axis_index=37)
    grid.save_fig(axis="z", axis_index=50)
    grid.plot_n(grid=grid, axis="y", axis_index=37)
    grid.plot_n(grid=grid, axis="z", axis_index=50)

    # 运行仿真
    grid.run()

    grid.save_fig(axis="y", axis_number=37, show_energy=True)

    # 绘制空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=37, folder=grid.folder)
    Grid.plot_field(grid=grid, field="E", field_axis="y", axis="y", axis_index=37, folder=grid.folder)
    Grid.plot_field(grid=grid, field="E", field_axis="z", axis="y", axis_index=37, folder=grid.folder)
    Grid.plot_field(grid=grid, field="H", field_axis="x", axis="y", axis_index=37, folder=grid.folder)
    Grid.plot_field(grid=grid, field="H", field_axis="y", axis="y", axis_index=37, folder=grid.folder)
    Grid.plot_field(grid=grid, field="H", field_axis="z", axis="y", axis_index=37, folder=grid.folder)

    # 保存仿真结果
    grid.save_simulation()
