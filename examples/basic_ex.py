from photfdtd import Waveguide, Grid, Index, fdtd

# fdtd.set_backend("numpy") # generate numpy backend
# fdtd.set_backend("torch") # generate torch backend
fdtd.set_backend("torch") # generate torch backend with cuda support (cuda must be installed)

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide 本示例展示了一个基础矩形波导的二维仿真
    # set background indexs and materials设置背景折射率
    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    index_SiO2 = Index(material="SiO2")
    index_Re_SiO2, index_Im_SiO2 = index_SiO2.get_refractive_index(wavelength=1.55e-6)
    background_index = index_Re_SiO2

    # # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=4e-6, grid_ylength=1, grid_zlength=8e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="basic_ex")

    # set waveguide 设置器件参数
    waveguide = Waveguide(
        xlength=400e-9, ylength=1, zlength=8e-6, refractive_index=index_Re_Si, name="waveguide", grid=grid
    )

    # add waveguide to grid 往 grid 里添加器件
    grid.add_object(waveguide)

    # set a line source with center wl at 1550nm. Set x (or y, z) = None to put the source at center coordinate
    # 设置一个线光源高斯脉冲，中心波长为1550nm。设置x（或y，z）= None将光源放置在中心坐标处
    grid.set_source(source_type="linesource",
                    wavelength=1550e-9, name="source", x=None, y=0, z=1200e-9, pulse_length=30e-15,
                    xlength=400e-9, ylength=0, zlength=0, polarization="x", pulse_type="gaussian")

    # set a line detector 设置一个线监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector1",
                      x=None,
                      y=0,
                      z=1500e-9,
                      xlength=400e-9,
                      ylength=0,
                      zlength=0
                      )
    grid.set_detector(detector_type="linedetector",
                      name="detector2",
                      x=None,
                      y=0,
                      z=7000e-9,
                      xlength=400e-9,
                      ylength=0,
                      zlength=0
                      )

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    # run the FDTD simulation, set animate = True to generate a video (ffmpeg required).
    # 运行仿真, 设置animate=True生成视频（需要安装ffmpeg）
    grid.run(animate=True, save=True, interval=20, time=200e-15)

    # Visualize the simulation results 可视化仿真结果
    grid.visualize()

    # Other plots
    grid.plot_field(field="E", field_axis="x", axis="y")
    grid.plot_field(field="E", field_axis="y", axis="y")
    grid.plot_field(field="E", field_axis="z", axis="y")
    grid.plot_field(field="H", field_axis="x", axis="y")
    grid.plot_field(field="H", field_axis="y", axis="y")
    grid.plot_field(field="H", field_axis="z", axis="y")

