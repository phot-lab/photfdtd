import utils
from photfdtd import DirectionalCoupler, Grid, Solve

if __name__ == "__main__":

    background_index = 1.455

    dc = DirectionalCoupler(
        xlength=200,
        ylength=80,
        zlength=20,
        x=100,
        y=50,
        z=12,
        direction=1,
        width=20,
        name="dc",
        refractive_index=3.47,
        xlength_rectangle=50,
        gap=10,
        background_index=background_index
    )

    grid = Grid(grid_xlength=200, grid_ylength=100, grid_zlength=25, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_dc")

    grid.set_source(source_type="planesource", period=1550e-9 / 299792458, waveform=False, x=25, y=80, z=12, xlength=0,
                    ylength=dc.width + 4, zlength=dc.width + 2)

    grid.set_detector(detector_type='blockdetector',
                      x=175, xlength=0,
                      y=80, ylength=dc.width + 4,
                      z=12, zlength=dc.width + 2,
                      name='detector')

    grid.add_object(dc)

    # 创建solve对象
    solve = Solve(grid=grid)

    solve.plot()

    grid.run()

    # 保存仿真结果
    grid.save_simulation()

    # 绘制任意截面场图
    grid.visualize(x=100, showEnergy=True, show=True, save=True)
    grid.visualize(z=12, showEnergy=True, show=True, save=True)

    # 读取仿真结果
    data = grid.read_simulation(folder=grid.folder)