import utils
from photfdtd import Arc, Grid, Solve

if __name__ == "__main__":

    background_index=1.0

    arc = Arc(outer_radius=300, zlength=1, x=500, y=500, z=0, width=20, refractive_index=3.47, name="arc", direction=4,
              background_index=background_index)

    grid = Grid(grid_xlength=1000, grid_ylength=1000, grid_zlength=1, grid_spacing=1550e-10, total_time=1,
                foldername="test_arc",
                permittivity=background_index ** 2)

    grid.add_object(arc)

    solve = Solve(grid=grid)

    solve._plot_(axis="z",
                 index=0,
                 filepath=grid.folder)

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    grid.save_fig(axis="z",
                  axis_number=0)