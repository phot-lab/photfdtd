from photfdtd import FWG, Arc, Grid, Solve, Waveguide

if __name__ == "__main__":
    background_index = 1.4447

    # 设置器件参数
    fwg = FWG(outer_radius=250, zlength=1, x=160, y=40, z=0, width=12, refractive_index=3.47, name="fwg",
              background_index=background_index, angle_psi=45, angle_phi=67.5, gap=12, number=10)

    waveguide = Waveguide(
        xlength=10, ylength=50, zlength=1, x=160, y=25, z=0, refractive_index=3.47, name="Waveguide",
        background_index=background_index
    )

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=320, grid_ylength=450, grid_zlength=1, grid_spacing=40e-9, total_time=1,
                foldername="test_fwg",
                pml_width_x=25,
                pml_width_y=25,
                pml_width_z=0,
                permittivity=background_index ** 2, )

    # 往 grid 里添加器件
    grid.add_object(fwg)
    grid.add_object(waveguide)

    grid.set_source(source_type="linesource", period=1300e-9 / 299792458, x=160, y=30, z=0,
                    xlength=15, ylength=1, zlength=1)



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
