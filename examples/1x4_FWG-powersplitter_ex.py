import utils
from photfdtd import FWG, Taper, Grid, Solve, Waveguide
# FIXME: Make this functional

if __name__ == "__main__":
    background_index = 1.444
    n_Si = 3.476

    # 设置器件参数
    # + n * 11
    number = 18
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=400, grid_ylength=300, grid_zlength=1, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_1x4_fwg")
    fwg1 = FWG(outer_radius=187 + (number - 14) * 11, zlength=1, x=90, y=150, z=0, width=6, refractive_index=n_Si,
               name="fwg1",
               grid=grid, angle_psi=28, angle_phi=-28, gap=5, number=number)
    fwg2 = FWG(outer_radius=187 + (number - 14) * 11, zlength=1, x=90, y=150, z=0, width=6, refractive_index=n_Si,
               name="fwg2",
               grid=grid, angle_psi=28, angle_phi=0, gap=5, number=number)

    waveguide = Waveguide(
        xlength=80, ylength=25, zlength=1, x=65, y=150, z=0, refractive_index=n_Si, name="Waveguide",
        grid=grid
    )
    waveguide1 = Waveguide(
        xlength=100, ylength=25, zlength=1, x=151 + 104 + 50, y=162, z=0, refractive_index=n_Si, name="Waveguide1",
        grid=grid
    )
    waveguide2 = Waveguide(
        xlength=100, ylength=25, zlength=1, x=151 + 104 + 50, y=138, z=0, refractive_index=n_Si, name="Waveguide2",
        grid=grid
    )
    waveguide3 = Waveguide(
        xlength=90, ylength=25, zlength=1, x=354, y=150, z=0, refractive_index=n_Si, name="Waveguide3",
        grid=grid
    )
    waveguide1.rotate_Z(angle=25, center=[-100, 12, 0])
    waveguide2.rotate_Z(angle=-25, center=[-100, 12, 0])
    # x=0 在x=104
    taper = Taper(xlength=91, width=5, ylength=25, zlength=1, x=149, y=150, z=0, name="taper", refractive_index=n_Si,
                  grid=grid)

    taper1 = Taper(xlength=100, width=5, ylength=25, zlength=1, x=104 + int(1048 / 20) + 50, y=162, z=0, name="taper1",
                   refractive_index=n_Si, grid=grid)
    taper2 = Taper(xlength=100, width=5, ylength=25, zlength=1, x=104 + int(1048 / 20) + 50, y=150 - 12, z=0,
                   name="taper2", refractive_index=n_Si, grid=grid)
    taper3 = Taper(xlength=100, width=5, ylength=25, zlength=1, x=260, y=150, z=0, name="taper3", refractive_index=n_Si,
                   grid=grid)
    taper1.rotate_Z(angle=25, center=[0, 12, 0])
    taper2.rotate_Z(angle=-25, center=[0, 12, 0])

    # 往 grid 里添加器件
    grid.add_object(fwg1)
    grid.add_object(fwg2)
    grid.add_object(waveguide)
    grid.add_object(waveguide1)
    grid.add_object(waveguide2)
    grid.add_object(waveguide3)
    grid.add_object(taper)
    grid.add_object(taper1)
    grid.add_object(taper2)
    grid.add_object(taper3)

    grid.set_source(source_type="linesource", wavelength=1550e-9, x=40, y=150, z=0,
                    xlength=1, ylength=20, zlength=1, polarization="z")
    grid.save_fig(axis="z", axis_number=0)

    grid.run(time=3000)
    grid.visualize()
    # grid.save_fig(axis="z",
    #               axis_number=0,
    #               show_geometry=False)
    Grid.plot_field(grid=grid, field="E", field_axis="z", axis="z", axis_index=0, folder=grid.folder)
