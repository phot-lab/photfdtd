import utils
from photfdtd import Ring, Grid, Index

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=15e-6, grid_ylength=1, grid_zlength=15e-6, grid_spacing=20e-9,
                permittivity=1 ** 2, foldername="test_ring_2D")

    ring = Ring(outer_radius=5e-6, ylength=1, width_s=400e-9, width_r=400e-9, length=0,
                gap=100e-9, name="ring", refractive_index=index_Re_Si, grid=grid)

    grid.set_source(source_type="linesource", wavelength=1540e-9, pulse_type="gaussian",waveform="gaussian",
                    x_start=2e-6, x_end=2.6e-6, y=0, z=2e-6,
                    ylength=1, zlength=1, polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=2e-6, x_end=2.6e-6, y=0, z=12e-6,
                      ylength=1, zlength=1,
                      name='detector1')

    grid.add_object(ring)
    grid.save_fig()
    grid.plot_n()

    grid.run(time=1000e-15)

    grid.save_simulation()
    # grid.read_simulation(grid.folder)
    grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    grid.detector_profile()
    grid.calculate_source_profile()
    grid.calculate_Transmission(field_axis="x", wl_start=1500e-9, wl_end=1600e-9)
    # 由监视器数据绘制Ex场随时间变化的图像
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=10, name_det="detector1")


