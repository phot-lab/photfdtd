import utils
from photfdtd import FWG, Waveguide, Grid, Solve

if __name__ == "__main__":
    background_index = 1.444
    n_Si = 3.476

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=20e-9,
                foldername="test_fwg_2D",
                permittivity=background_index ** 2,)

    # 设置器件参数
    fwg = FWG(outer_radius=80 * 20e-9, zlength=1 * 20e-9, width=5 * 40e-9, refractive_index=n_Si, name="fwg",
              grid=grid, angle_psi=120, angle_phi=30, gap=6, number=4)

    # waveguide = Waveguide(
    #     xlength=10, ylength=50, zlength=1, x=160, y=25, z=0, refractive_index=n_Si, name="Waveguide",
    #     grid=grid
    # )

    # 往 grid 里添加器件
    grid.add_object(fwg)

    grid.set_source(source_type="pointsource", period=850e-9 / 299792458, x=100, y=100, z=0, polarization="x")

    solve = Solve(grid=grid,
                  axis='z',
                  index=0,
                  filepath=grid.folder
                  )
    grid.save_fig(axis="z", axis_number=0)

    # 绘制任一截面
    solve.plot()

    # grid.run()

    # # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="z", axis_index=0, folder=grid.folder)


