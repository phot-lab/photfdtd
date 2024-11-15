import utils
from photfdtd import Cone, Grid

if __name__ == "__main__":
    # 单模光纤模式分析
    # 单模光纤，参数：
    # 包层折射率：1.4437
    # 纤芯折射率：1.4504
    # 纤芯半径：4um
    # Pml边界厚度：3um
    # 波长：1.55um

    background_index = 1.4437

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=40e-6, grid_ylength=40e-6, grid_zlength=40e-6, grid_spacing=200e-9,
                foldername="test_cone", permittivity=background_index ** 2)
    fiber = Cone(length=40e-6, radius_upper=10e-6, radius_lower=0e-6, refractive_index=1.4555,
                  name='cone', axis='y', grid=grid)

    # 往 grid 里添加fiber
    grid.add_object(fiber)
    grid.save_fig(axis="x", axis_number=100)
    grid.save_fig(axis="x", axis_number=50)
    grid.save_fig(axis="x", axis_number=150)
    grid.save_fig(axis="y", axis_number=100)
    grid.save_fig(axis="y", axis_number=50)
    grid.save_fig(axis="y", axis_number=150)
    grid.save_fig(axis="z", axis_number=100)
    grid.save_fig(axis="z", axis_number=50)
    grid.save_fig(axis="z", axis_number=150)
    grid.plot_n(grid=grid, axis="y", axis_index=100)
