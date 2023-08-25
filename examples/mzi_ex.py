import utils
from photfdtd import Mzi, Grid, Solve

if __name__ == "__main__":

    background_index = 1.0

    mzi = Mzi(gap=10,
              xlength_dc=50,
              zlength=1,
              x=100,
              y=100,
              z=0,
              width=4,
              refractive_index=3.47,
              name='mzi',
              couplelength=60,
              addlength_arm1=40,
              addlength_arm2=21,
              couplelength_dc=10,
              gap_dc=2,
              background_index=background_index)

    grid = Grid(grid_xlength=200, grid_ylength=200, grid_zlength=1, grid_spacing=10e-9, total_time=1,
                pml_width_x=1,
                pml_width_y=1, pml_width_z=0, foldername="test_mzi", permittivity=background_index ** 2)

    grid.add_object(mzi)

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制x=50截面
    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    grid.run()

    # 保存画好的图
    grid.save_fig(axis="z",
                  axis_number=0)
