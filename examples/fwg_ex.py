from photfdtd import FWG, Arc, Grid, Solve

if __name__ == "__main__":
    background_index = 1.444
    n_Si = 3.476

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=20e-9, total_time=1,
                foldername="test_fwg",
                pml_width_x=25,
                pml_width_y=25,
                pml_width_z=0,
                permittivity=background_index ** 2,)

    # 设置器件参数
    fwg = FWG(outer_radius=150 * 40e-9, zlength=1 * 40e-9, width=12 * 40e-9, refractive_index=n_Si, name="fwg",
              grid=grid, angle_psi=45, angle_phi=67.5, gap=12, number=5)

    waveguide = Waveguide(
        xlength=10, ylength=50, zlength=1, x=160, y=25, z=0, refractive_index=n_Si, name="Waveguide",
        grid=grid
    )

    # 往 grid 里添加器件
    grid.add_object(fwg)

    grid.set_source(source_type="pointsource", period=850e-9 / 299792458, x=65, y=75, z=0)

    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )

    # 绘制任一截面
    solve.plot()

    grid.run()
    grid.save_fig(axis="z",
                  axis_number=0)
