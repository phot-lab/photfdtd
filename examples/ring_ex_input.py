from photfdtd import Grid, Index, Waveguide, fdtd
fdtd.set_backend("torch.cuda")

if __name__ == "__main__":
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)
    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)

    grid = Grid(grid_xlength=2e-6, grid_ylength=2.5e-6, grid_zlength=2e-6, grid_spacing=40e-9, permittivity=1 ** 2,
                foldername="test_ring_input")
    grid.set_source(source_type="linesource", wavelength=1550e-9, pulse_type="gaussian",waveform="gaussian",
                    x_start=0.8e-6,x_end=1.2e-6,
                    xlength=0.4e-6,ylength=0, zlength=0, polarization="x")

    grid.set_detector(detector_type='linedetector',
                      x_start=0.8e-6,x_end=1.2e-6, z=1.0e-6,
                      ylength=1, zlength=1,
                      name='detector_input')

    input_waveguide = Waveguide(xlength=400e-9, ylength=200e-9,zlength=2e-6,refractive_index=index_Re_Si, grid=grid)
    grid.add_object(input_waveguide)
    grid.save_fig()
    grid.plot_n()

    # 总时间需与ring_ex.py中设置的时间一致
    # The total time should match the time set in ring_ex.py
    grid.run(animate=False, time=4000e-15, save=True, interval=100)
    # grid.animate()
    # grid = grid.read_simulation(grid.folder)

    grid.visualize()
    # grid.save_fig(axis="y", axis_number=0, show_energy=True)
    # # 绘制仿真结束时刻空间场分布
    # Grid.plot_field(grid=grid, field="E", field_axis="x", axis="y", axis_index=0, folder=grid.folder)
    # Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")
    # grid.detector_profile()
    # grid.calculate_source_profile()
