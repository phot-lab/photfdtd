import utils
from photfdtd import Waveguide, Grid, Solve, constants

if __name__ == "__main__":
    background_index = 1.0

    # 点光源案例

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=100, grid_ylength=100, grid_zlength=1,
                grid_spacing=20e-9,
                total_time=200,
                pml_width_x=10,
                pml_width_y=10,
                pml_width_z=1,
                permittivity=background_index ** 2,
                foldername="test_pointsource")

    # 设置光源
    grid.set_source(source_type="pointsource", wavelength=1550e-9, name="source", x=50, y=50, z=1,
                    xlength=0, ylength=0, zlength=0)

    # 运行仿真
    grid.run()

    # 绘制截面场图
    grid.visualize(z=0, showEnergy=True, show=True, save=True)

    # 绘制仿真结束时刻空间场分布
    Grid.plot_field(grid=grid, field="E", field_axis=2, axis="z", axis_index=0, folder=grid.folder)
