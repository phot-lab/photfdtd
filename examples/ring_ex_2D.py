import utils
from photfdtd import Ring, Grid, Index, Waveguide

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=15e-6, grid_ylength=1, grid_zlength=15e-6, grid_spacing=50e-9,
                permittivity=1 ** 2, foldername="test_ring_2D")

    ring = Ring(outer_radius=5e-6, ylength=1, width_s=400e-9, width_r=400e-9, length=0, length_s=15e-6,
                gap=50e-9, name="ring", refractive_index=index_Re_Si, grid=grid)
    grid.set_PML(pml_width=1.5e-6)
    grid.set_source(source_type="linesource", wavelength=1570e-9, pulse_type="gaussian",waveform="gaussian",
                    x_start=2e-6, x_end=2.4e-6, y=0, z=2e-6,
                    ylength=1, zlength=1, polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, x_end=2.7e-6, y=0, z=3e-6,
                      ylength=1, zlength=1,
                      name='detector1')
    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, x_end=2.7e-6, y=0, z=13.2e-6,
                      ylength=1, zlength=1,
                      name='detector2')
    grid.add_object(ring)

    grid.save_fig()
    grid.plot_n()
    #
    # grid.run(time=1000e-15)
    # # # #
    # grid.save_simulation()
    grid = Grid.read_simulation(grid.folder)
    # grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    # grid.detector_profile()
    # grid.calculate_source_profile()
    grid.calculate_Transmission(detector_name_1="detector1", detector_name_2="detector2")
    grid.visualize()
    # 由监视器数据绘制Ex场随时间变化的图像
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=10, name_det="detector1")


