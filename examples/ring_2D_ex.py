from photfdtd import Ring, Grid, Index, fdtd, Waveguide
# It's recommended to use torch.cuda to simulate a ring.
fdtd.set_backend("torch.cuda")

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=11e-6, grid_ylength=1, grid_zlength=10e-6, grid_spacing=40e-9, permittivity=1 ** 2,
                foldername="test_ring_2D")

    # Pml will be automatically set to wavelength/2 in all directions when set source. One can also set PML manually.
    # 当设置光源时，PML会自动设置为所有方向上的波长的一半。也可以手动设置PML。
    ring = Ring(outer_radius=3.3e-6, ylength=1, width_s=400e-9, width_r=400e-9, length=0e-6, length_s=10e-6,
                gap=100e-9, name="ring", refractive_index=index_Re_Si, grid=grid)

    grid.set_source(source_type="linesource", wavelength=1550e-9, pulse_type="gaussian",waveform="gaussian",
                    x_start=1.7e-6,x_end=2.1e-6, z=1.0e-6,
                    xlength=0.4e-6,ylength=0, zlength=0, polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, x_end=2.1e-6, z=1.0e-6,
                      ylength=1, zlength=1,
                      name='detector1')
    grid.set_detector(detector_type='linedetector',
                      x_start=1.7e-6, x_end=2.1e-6, z=9e-6,
                      ylength=1, zlength=1,
                      name='detector2')
    grid.set_detector(detector_type='linedetector',
                      x_start=8.9e-6, x_end=9.3e-6, z=1e-6,
                      ylength=1, zlength=1,
                      name='detector3')
    grid.set_detector(detector_type='linedetector',
                      x_start=8.9e-6, x_end=9.3e-6, z=9e-6,
                      ylength=1, zlength=1,
                      name='detector4')
    grid.add_object(ring)

    grid.save_fig()
    grid.plot_n()
    #
    grid.run(animate=True, time=4000e-15, save=True, interval=20)

    # grid._grid.time_steps_passed = 10000
    grid.visualize()
    # grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    # grid.detector_profile()
    # grid.calculate_source_profile()
    """ 要获得准确的透射谱或S参数谱线，运行ring_ex_input.py，将得到的detector_input的.h5文件放入本脚本的结果文件夹，
    然后运行S parameters.py。
    To obtain accurate transmission spectra or S-parameter spectra, run ring_ex_input.py,
    place the resulting detector_input.h5 file into the results folder of this script,
    and then run S parameters.py.
    """
    freqs, spectrum1 = grid.visualize_single_detector(name_det="detector1")
    freqs, spectrum2 = grid.visualize_single_detector(name_det="detector2")
    freqs, spectrum3 = grid.visualize_single_detector(name_det="detector3")
    freqs, spectrum4 = grid.visualize_single_detector(name_det="detector4")

    import matplotlib.pyplot as plt

    plt.plot(freqs, abs(spectrum2 / spectrum1) ** 2)
    plt.ylabel("Ex")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_2"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()

    plt.plot(freqs, abs(spectrum3 / spectrum1) ** 2)
    plt.ylabel("Ex")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_3"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()

    plt.plot(freqs, abs(spectrum4 / spectrum1) ** 2)
    plt.ylabel("Ex")
    plt.xlabel("frequency (THz)")
    plt.title("Transmission calculated by Ex^2")
    plt.legend()
    file_name = "Transmission_detector_4"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()
    # 由监视器数据绘制Ex场随时间变化的图像


