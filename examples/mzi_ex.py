import utils
from photfdtd import Mzi, Grid, Solve, Ysplitter, constants

if __name__ == "__main__":
    background_index = 1.0

    mzi = Mzi(gap=50,
              xlength_dc=100,
              zlength=1,
              x=350,
              y=175,
              z=0,
              width=20,
              refractive_index=3.47,
              name='mzi',
              couplelength=150,
              addlength_arm1=0,
              addlength_arm2=0,
              couplelength_dc=10,
              gap_dc=10,
              background_index=background_index)

    ysplitter1 = Ysplitter(xlength=125,
                           ylength=90,
                           zlength=1,
                           x=99,
                           y=175,
                           z=0,
                           direction=1,
                           width=20,
                           name="ysplitter1",
                           refractive_index=3.47,
                           xlength_waveguide=30,
                           xlength_taper=40,
                           ylength_taper=40,
                           width_sbend=20,
                           background_index=background_index)

    ysplitter2 = Ysplitter(xlength=125,
                           ylength=90,
                           zlength=1,
                           x=599,
                           y=175,
                           z=0,
                           direction=-1,
                           width=20,
                           name="ysplitter2",
                           refractive_index=3.47,
                           xlength_waveguide=30,
                           xlength_taper=40,
                           ylength_taper=40,
                           width_sbend=20,
                           background_index=background_index)

    grid = Grid(grid_xlength=700, grid_ylength=350, grid_zlength=1, grid_spacing=20e-9, total_time=4000,
                pml_width_x=50,
                pml_width_y=30, pml_width_z=0,
                foldername="test_mzi", permittivity=background_index ** 2)

    grid.add_object(mzi)
    # grid.add_object(ysplitter1)
    grid.add_object(ysplitter2)

    # 设置光源
    grid.set_source(source_type="linesource",
                    period=1550e-9/constants.c,
                    name="source",
                    pulse_type="none",
                    x=70,
                    y=175,
                    z=0,
                    xlength=1,
                    ylength=18,
                    zlength=1
                    )

    # 设置监视器
    grid.set_detector(detector_type="linedetector",
                      name="detector",
                      x=630,
                      y=175,
                      z=0,
                      xlength=1,
                      ylength=22,
                      zlength=1
                      )

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve._plot_(axis='z',
                 index=0,
                 filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.save_fig(axis="z",
                  axis_number=0)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)
