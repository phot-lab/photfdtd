from photfdtd import Waveguide, Grid, Solve, Index

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide 本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1

    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    # # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=3e-6, grid_ylength=1, grid_zlength=3e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="planesource_ex")

    # set a line source with center wl at 1550nm
    grid.set_source(source_type="planesource",
                    wavelength=1550e-9, name="source", axis="y", waveform="gaussian", pulse_type="gaussian",
                    xlength=1000e-9, ylength=0, zlength=1000e-9, polarization="x")

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    # run the FDTD simulation 运行仿真
    grid.run(animate=True, save=True, interval=20,  time=1000)
    grid.plot_field(grid=grid, field="E")
    grid.save_fig(show_energy=True)
    grid.visualize()
