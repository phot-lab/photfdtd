import utils
from photfdtd import Ring, Grid, Index, Waveguide

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=15e-6, grid_ylength=2.5e-6, grid_zlength=20e-6, grid_spacing=40e-9, permittivity=index_Re_SiO2 ** 2,
                foldername="test_ring")
    grid.set_PML(pml_width_y=0.8e-6, pml_width_x=0.8e-6, pml_width_z=0.8e-6)
    ring = Ring(outer_radius=5e-6, ylength=0.22e-6, width_s=400e-9, width_r=400e-9, length=4e-6, length_s=20e-6,
                gap=40e-9, name="ring", refractive_index=index_Re_Si, grid=grid)

    grid.set_source(source_type="linesource", wavelength=1550e-9, pulse_type="gaussian",waveform="gaussian",
                    x_start=2.1e-6, x_end=2.5e-6, z=2e-6,
                    ylength=1, zlength=1, polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, x_end=2.7e-6, z=3e-6,
                      ylength=1, zlength=1,
                      name='detector1')
    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, x_end=2.7e-6, z=15e-6,
                      ylength=1, zlength=1,
                      name='detector2')
    grid.set_detector(detector_type='linedetector',
                      x_start=12.3e-6, x_end=13.3e-6, z=3e-6,
                      ylength=1, zlength=1,
                      name='detector3')
    grid.set_detector(detector_type='linedetector',
                      x_start=12.3e-6, x_end=13.3e-6, z=15e-6,
                      ylength=1, zlength=1,
                      name='detector4')
    grid.add_object(ring)
    print(grid._grid.time_step)
    grid.save_fig(axis_index=31)
    grid.plot_n(axis_index=31)
    #
    # grid.run(animate=True, time=10000, save=True, interval=20)
    # grid.animate()
    # grid = grid.read_simulation(grid.folder)
    grid._grid.time_steps_passed = 10000
    grid.visualize()
    # grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    # grid.detector_profile()
    # grid.calculate_source_profile()
    freqs, spectrum1 = grid.visualize_single_detector(name_det="detector1")
    freqs, spectrum2 = grid.visualize_single_detector(name_det="detector2")
    freqs, spectrum3 = grid.visualize_single_detector(name_det="detector3")
    freqs, spectrum4 = grid.visualize_single_detector(name_det="detector4")

    import matplotlib.pyplot as plt

    plt.plot(freqs, (spectrum2 / spectrum1) ** 2)
    plt.ylabel("Ex")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_2"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()

    plt.plot(freqs, (spectrum3 / spectrum1) ** 2)
    plt.ylabel("Ex")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_3"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()

    plt.plot(freqs, (spectrum4 / spectrum1) ** 2)
    plt.ylabel("Ex")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_4"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()
    # 由监视器数据绘制Ex场随时间变化的图像


