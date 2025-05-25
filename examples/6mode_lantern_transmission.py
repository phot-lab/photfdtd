import numpy as np
import utils
from photfdtd import Grid, Lantern_6Mode, Solve, OverlapCalculator
import matplotlib.pyplot as plt
import os

if __name__ == "__main__":
    # 定义不同的taper_ratio值
    taper_ratios = [1, 0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.16]
    background_index = 1.438

    # 创建主文件夹以保存所有结果
    main_folder_path = "6mode_lantern_transimision_1"
    if not os.path.exists(main_folder_path):
        os.makedirs(main_folder_path)
    mode_data = {}

    for taper_ratio in taper_ratios:
        # 创建子文件夹以标注taper_ratio，但实际保存结果到主文件夹
        folder_path = os.path.join(main_folder_path, f"taper_ratio_{taper_ratio}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 创建Grid对象
        grid = Grid(
            grid_xlength=125e-6 ,
            grid_ylength=125e-6 ,
            grid_zlength=1,
            grid_spacing=312.5e-9,
            foldername=folder_path,
            permittivity=background_index ** 2
        )

        # 实例化Lantern_6Mode对象
        lantern = Lantern_6Mode(
            length=1,
            r_LP01=4.25e-6,
            r_LP11a=3.75e-6,
            r_LP11b=3.5e-6,
            r_LP21a=3.25e-6,
            r_LP21b=3.1e-6,
            r_LP02=2.5e-6,
            r=34.5e-6,
            taper_ratio=taper_ratio,
            n_LP01=1.45,
            n_LP11a=1.45,
            n_LP11b=1.45,
            n_LP21a=1.45,
            n_LP21b=1.45,
            n_LP02=1.45,
            n_cladding=1.444,
            r_cladding=55e-6,
            axis="z",
            grid=grid,
            priority=[1, 1, 1, 1, 1, 1, 1],
            name="lantern_6mode"
        )

        # 往grid里添加fiber
        grid.add_object(lantern)

        # 创建solve对象
        solve = Solve(
            grid=grid,
            axis="z",
            filepath=folder_path,  # 结果保存到子文件夹
            index=0
        )

        # 绘制折射率分布
        solve.plot()

        # 计算截面
        data = solve.calculate_mode(
            lam=1550e-9, neff=1.45, neigs=2,
            x_boundary_low="pml", y_boundary_low="pml",
            x_boundary_high="pml", y_boundary_high="pml",
            background_index=background_index
        )

        # 保存模式，文件名不包含taper_ratio
        Solve.draw_mode(filepath=solve.filepath, data=data, content="amplitude")

        # 将模式数据保存到 mode_data 字典中
        mode_data[taper_ratio] = data

    # 提取电场数据并计算重叠积分
    E1_data = mode_data[1]
    E2_data = mode_data[0.16]

    # 创建并计算重叠积分
    overlap_calculator = OverlapCalculator(grid_spacing=312.5e-9, E1_data=E1_data, E2_data=E2_data)

