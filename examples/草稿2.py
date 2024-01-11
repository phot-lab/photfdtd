from photfdtd import Waveguide, Arc, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    arc = Arc(outer_radius=60, zlength=1, x=100, y=100, z=0, width=4, refractive_index=3.47, name="arc",
              background_index=background_index, angle_phi=-90, angle_psi=180)
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=20e-9, total_time=1,
                foldername="test_0110",
                pml_width_x=25,
                pml_width_y=25,
                pml_width_z=0,
                permittivity=background_index ** 2, )

    # 往 grid 里添加器件
    grid.add_object(arc)
    # create a Solve object. You can use it to solve the eigenmodes (see eigenmode_solver_ex) 创建solve对象
    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )

    # plot the refractive index map on z=0绘制z=0截面折射率分布
    solve.plot()

    # run the FDTD simulation 运行仿真
    grid.run()
    # We can plot the field after simulation绘制z=0截面场图
    grid.save_fig(axis="z",
                  axis_number=0,
                  geo=solve.geometry)
