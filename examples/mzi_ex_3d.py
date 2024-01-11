import utils
from photfdtd import Mzi, Grid, Solve, Ysplitter, constants

if __name__ == "__main__":
    background_index = 1.0

    mzi = Mzi(gap=50,
              xlength_dc=150,
              zlength=25,
              x=380,
              y=125,
              z=20,
              width=10,
              refractive_index=3.47,
              name='mzi',
              couplelength=100,
              addlength_arm1=0,
              addlength_arm2=0,
              couplelength_dc=10,
              gap_dc=10,
              background_index=background_index)


    # 设置y分支波导时应给s波导之间留有一定间距，否则光场可能在连接处反复振荡导致数值过大而报错
    ysplitter1 = Ysplitter(xlength=180,
                           ylength=70,
                           zlength=25,
                           x=80,
                           y=125,
                           z=20,
                           direction=1,
                           width=10,
                           name="ysplitter1",
                           refractive_index=3.47,
                           xlength_waveguide=60,
                           xlength_taper=40,
                           ylength_taper=24,
                           width_sbend=10,
                           background_index=background_index)

    # ysplitter2 = Ysplitter(xlength=150,
    #                        ylength=90,
    #                        zlength=1,
    #                        x=650,
    #                        y=125,
    #                        z=0,
    #                        direction=-1,
    #                        width=20,
    #                        name="ysplitter2",
    #                        refractive_index=3.47,
    #                        xlength_waveguide=30,
    #                        xlength_taper=40,
    #                        ylength_taper=44,
    #                        width_sbend=20,
    #                        background_index=background_index)

    grid = Grid(grid_xlength=600, grid_ylength=250, grid_zlength=40, grid_spacing=20e-9, total_time=3000,
                pml_width_x=40,
                pml_width_y=10, pml_width_z=0,
                foldername="test_mzi_1023", permittivity=background_index ** 2)

    grid.add_object(mzi)
    grid.add_object(ysplitter1)
    # grid.add_object(ysplitter2)

    # 设置光源
    grid.set_source(source_type="pointsource", period=1550e-9 / constants.c, name="source", pulse_type="none", x=50,
                    y=125, z=20, xlength=1, ylength=16, zlength=30)

    # 设置监视器
    # grid.set_detector(detector_type="blockdetector",
    #                   name="detector",
    #                   x=110,
    #                   y=125,
    #                   z=20,
    #                   xlength=100,
    #                   ylength=60,
    #                   zlength=1
    #                   )

    # 创建solve对象
    solve = Solve(grid=grid)

    # 绘制任一截面折射率分布
    solve.plot(axis='z',
               index=20,
               filepath=grid.folder)

    # 运行仿真
    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # z=0截面场图
    grid.visualize(x=99, showEnergy=True, show=True, save=True)
    grid.visualize(z=10, showEnergy=True, show=True, save=True)
    grid.visualize(z=15, showEnergy=True, show=True, save=True)
    grid.visualize(z=20, showEnergy=True, show=True, save=True)
    grid.visualize(z=25, showEnergy=True, show=True, save=True)
    # grid.visualize_detector("detector", "x", "E", show=True, save=True)
    # grid.visualize_detector("detector", "y", "E", show=True, save=True)
    # grid.visualize_detector("detector", "z", "E", show=True, save=True)
    # grid.save_fig(axis="z", axis_number=20)
    # grid.save_fig(axis="z", axis_number=10)
    # grid.save_fig(axis="z", axis_number=30)

    # 读取仿真结果
    # data = grid.read_simulation(folder=grid.folder)
