import photfdtd
from photfdtd import Arc, Grid, Waveguide
from photfdtd.fdtd import constants
photfdtd.fdtd.set_backend("numpy")  # 设置后端为torch

if __name__ == "__main__":
    background_index = 1.5
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=20, grid_zlength=200, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_arc")
    grid.set_PML(pml_width_x=0.8e-6, pml_width_y=0, pml_width_z=0.8e-6)
    # 设置器件参数
    waveguide1 = Waveguide(
        xlength=1e-6, ylength=20, zlength=400e-9, x=1.5e-6, y=10, z=3.0e-6, refractive_index=3.47, name="Waveguide1",
        grid=grid
    )
    arc = Arc(outer_radius=60 * 20e-9, ylength=10, width=20, refractive_index=3.47, name="arc", angle_phi=0,
              angle_psi=90, grid=grid, angle_unit=True)
    waveguide2 = Waveguide(
        xlength=400e-9, ylength=20, zlength=1e-6, x=3e-6, y=10, z=1.5e-6, refractive_index=3.47, name="Waveguide2",
        grid=grid
    )

    # 往 grid 里添加器件
    grid.add_object(arc)
    grid.add_object(waveguide2)
    grid.add_object(waveguide1)

    # 设置光源
    grid.set_source(source_type="linesource", period=1550e-9 / constants.c, name="source",
                    x=waveguide2.x_center, y=10, z=1.0e-6,
                    xlength=400e-9, ylength=0, zlength=0, polarization="x")

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=150,
    #                   y=30,
    #                   z=11,
    #                   xlength=waveguide2.xlength + 4,
    #                   ylength=1,
    #                   zlength=waveguide1.zlength
    #                   )

    # We can plot the geometry now
    grid.save_fig()
    grid.plot_n()
    #
    # # 运行仿真
    grid.run(time=1000, save=True)
    #
    # 可视化
    grid.visualize()

