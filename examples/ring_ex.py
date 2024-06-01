import utils
from photfdtd import Ring, Grid, Index, Waveguide

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=11e-6, grid_ylength=1e-6, grid_zlength=10e-6, grid_spacing=45e-9,
                permittivity=1 ** 2, foldername="test_ring")

    ring = Ring(outer_radius=3.3e-6, ylength=0.18e-6, width_s=400e-9, width_r=400e-9, length=0,
                y=0.54e-6,
                gap=100e-9, name="ring", refractive_index=index_Re_Si, grid=grid)

    substrate = Waveguide(grid=grid, xlength=11e-6, ylength=45e-8, zlength=10e-6, refractive_index=index_Re_SiO2,
                          y=22.5e-8)

    grid.set_source(source_type="planesource", wavelength=1550e-9, pulse_type="None", waveform="gaussian",
                    x=9.1e-6, z=1.5e-6,
                    xlength=0.6e-6, ylength=0.5e-6,
                    axis="z", polarization="x")

    grid.set_detector(detector_type='blockdetector',
                      x=9.1e-6, z=8e-6,
                      xlength=0.6e-6, ylength=0.5e-6,
                      axis="z",
                      name='detector1')

    grid.add_object(ring)
    grid.add_object(substrate)
    grid.save_fig(axis="y", axis_index=11)
    grid.save_fig(axis="z", axis_index=100)
    grid.plot_n(axis="y", axis_index=11)
    grid.plot_n(axis="z", axis_index=100)

    grid.run(time=5000e-15)

    grid.save_simulation()

    grid.save_fig(show_energy=True)
    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder,
                    vmax=2, vmin=-2)

    # 读取仿真结果
    data = Grid.read_simulation(folder=grid.folder)

    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")