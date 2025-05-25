import utils
from photfdtd import Ring, Grid, Index, Waveguide

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=2e-6, grid_ylength=1, grid_zlength=2e-6, grid_spacing=20e-9, permittivity=1 ** 2,
                foldername="test_ring_0401_input")
    grid.set_PML(pml_width_y=0e-6, pml_width_x=0.8e-6, pml_width_z=0.8e-6)
    grid.set_source(source_type="linesource", wavelength=1550e-9, pulse_type="gaussian",waveform="gaussian",
                    x_start=0.8e-6,x_end=1.2e-6,
                    xlength=0.4e-6,ylength=0, zlength=0, polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=0.8e-6,x_end=1.2e-6, z=1.0e-6,
                      ylength=1, zlength=1,
                      name='detector_input')

    input_waveguide = Waveguide(xlength=400e-9, ylength=1,zlength=2e-6,refractive_index=index_Re_Si, grid=grid)
    grid.add_object(input_waveguide)
    grid.save_fig()
    grid.plot_n()
    #
    grid.run(animate=False, time=10000e-15, save=True, interval=100)
    # grid.animate()
    # grid = grid.read_simulation(grid.folder)

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


