from photfdtd import Mzi, Grid, Index, fdtd
fdtd.set_backend("numpy")

if __name__ == "__main__":
    background_index = 1.4447

    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=5e-6, grid_ylength=1, grid_zlength=18e-6, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="MZI_ex")

    mzi = Mzi(xlength=2e-6,
              ylength=1,
              zlength_DC=6e-6,
              couplelength_DC=3e-6,
              width_1=500e-9,
              width_2=500e-9,
              couplelength=1.5e-6,
              gap_DC=40e-9,
              name="MZI",
              refractive_index=index_Re_Si,
              grid=grid)

    grid.add_object(mzi)

    # 设置监视器
    # grid.set_detector(detector_type="linedetector",
    #                   name="detector",
    #                   x=680,
    #                   y=200,
    #                   z=0,
    #                   xlength=1,
    #                   ylength=22,
    #                   zlength=1
    #                   )

    grid.set_source(source_type="linesource",
                    wavelength=1550e-9, name="source", x=1600e-9, y=0, z=2100e-9,
                    xlength=400e-9, ylength=0, zlength=0, polarization="x")

    # # run the FDTD simulation 运行仿真
    grid.plot_n()
    grid.run(save=True)

    grid.visualize()


