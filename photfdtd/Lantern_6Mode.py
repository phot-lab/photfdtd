import numpy as np
from photfdtd import Waveguide
import math

class Lantern_6Mode(Waveguide):
    """
    六模光子灯笼
    x, y, z: 中心坐标
    r_LP01:纤芯1半径
    r_LP11a:纤芯2半径
    r_LP11b:纤芯3半径
    r_LP21a:纤芯4半径
    r_LP21b:纤芯5半径
    r_LP02:纤芯6半径
    n_LP01:纤芯1折射率
    n_LP11a:纤芯2折射率
    n_LP11b:纤芯3折射率
    n_LP21a:纤芯4折射率
    n_LP21b:纤芯5折射率
    n_LP02:纤芯6折射率
    n_cladding:包层折射率
    r_cladding:包层半径
    taper_ratio:拉锥比
    """

    def __init__(self, grid, x: int or float = None,
                 y: int or float = None,
                 z: int or float = None,length=100, r=50e-6,
                 r_LP01=100e-6, r_LP11a=100e-6, r_LP11b=100e-6, r_LP21a=100e-6, r_LP21b=100e-6, r_LP02=100e-6,
                 n_LP01=1.45, n_LP11a=1.46, n_LP11b=1.47, n_LP21a=1.48, n_LP21b=1.49, n_LP02=1.50, n_cladding=1.44, r_cladding=62.5e-6,
                 taper_ratio=0.1, name="lantern_6mode", axis="z", priority=[1, 1, 1, 1, 1, 1]):
        # 自动选择仿真区域中心
        self.x = x if x is not None else int(grid._grid_xlength / 2)
        self.y = y if y is not None else int(grid._grid_ylength / 2)
        self.z = z if z is not None else int(grid._grid_zlength / 2)
        # 处理输入参数的单位统一化
        length, _, _, _ = grid._handle_unit([length, 0, 0, 0], grid_spacing=grid._grid.grid_spacing)
        r = grid._handle_unit([r], grid_spacing=grid._grid.grid_spacing)[0]
        r_LP01, r_LP11a, r_LP11b, r_LP21a, r_LP21b, r_LP02, r_cladding = grid._handle_unit([r_LP01, r_LP11a, r_LP11b, r_LP21a, r_LP21b, r_LP02, r_cladding], grid_spacing=grid._grid.grid_spacing)

        # 定义 background_index 属性
        self.background_index = 1.438  # 根据你的需求设置相应的值
        # 定义_internal_objects属性
        self._internal_objects = [self]

        # 计算正五边形的各个顶点坐标
        cos_18 = math.cos(math.radians(18))
        sin_54 = math.sin(math.radians(54))
        cos_54 = math.cos(math.radians(54))
        sin_18 = math.sin(math.radians(18))
        actual_r = r * taper_ratio
        # x_center = grid._grid_xlength / 2  # 将 x_center 设置为仿真空间的一半
        # y_center = grid._grid_ylength / 2  # 将 y_center 设置为仿真空间的一半
        x1 = int(self.x-actual_r * cos_18)
        y1 = int(self.y+actual_r* sin_18)
        x2 = int(self.x+actual_r * cos_18)
        y2 = int(self.y+actual_r * sin_18)
        x3 = int(self.x-actual_r * cos_54)
        y3 = int(self.y-actual_r * sin_54)
        x4 = int(self.x)
        y4 = int(self.y+actual_r)
        x5 = int(self.x+actual_r * cos_54)
        y5 = int(self.y-actual_r * sin_54)
        x6 = int(self.x)
        y6 = int(self.y)


        # 计算纤芯半径和包层半径
        actual_r_LP01 = r_LP01 * taper_ratio
        actual_r_LP11a = r_LP11a * taper_ratio
        actual_r_LP11b = r_LP11b * taper_ratio
        actual_r_LP21a = r_LP21a * taper_ratio
        actual_r_LP21b = r_LP21b * taper_ratio
        actual_r_LP02 = r_LP02 * taper_ratio
        actual_r_cladding = r_cladding * taper_ratio

        # 初始化 xlength、ylength 和 zlength 属性
        self.xlength = int(2 * actual_r_cladding)
        self.ylength = int(2 * actual_r_cladding)
        self.zlength = length


        # 计算介电常数矩阵
        permittivity = self.compute_permittivity(grid, length, self.x, self.y, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6,
                                                  actual_r_LP01, actual_r_LP11a, actual_r_LP11b, actual_r_LP21a, actual_r_LP21b, actual_r_LP02,
                                                  actual_r_cladding, n_LP01, n_LP11a, n_LP11b, n_LP21a, n_LP21b, n_LP02, n_cladding)
        # 保存属性值
        self.permittivity = permittivity
        self.priority = priority
        self.n_cladding = n_cladding
        self.name = name
        self.length = length
        self.axis = axis
        self.priority = priority
        self.refractive_index = [n_LP01, n_LP11a, n_LP11b, n_LP21a, n_LP21b, n_LP02, n_cladding]

        # 初始化其他属性
        self.x = int(grid._grid_xlength / 2 - actual_r_cladding)
        self.y = int(grid._grid_ylength / 2 - actual_r_cladding)
        self.z = int(grid._grid_zlength / 2 - length / 2)

        # 计算优先级矩阵
        self._compute_priority()

    def compute_permittivity(self, grid, length, x_center, y_center, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6,
                             actual_r_LP01, actual_r_LP11a, actual_r_LP11b, actual_r_LP21a, actual_r_LP21b, actual_r_LP02,
                             actual_r_cladding, n_LP01, n_LP11a, n_LP11b, n_LP21a, n_LP21b, n_LP02, n_cladding):
        # 初始化介电常数矩阵
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength)) + self.background_index ** 2

        # 计算包层区域
        for j in range(self.xlength):
            for k in range(self.ylength):
                # 计算光子灯笼对象在仿真区域中的位置
                x_index = int(x_center + j - self.xlength // 2)
                y_index = int(y_center + k - self.ylength // 2)

                # 包层
                if (x_index - x_center) ** 2 + (y_index - y_center) ** 2 <= actual_r_cladding ** 2:
                    permittivity[j, k, :] = n_cladding ** 2


        # 计算纤芯区域
        for j in range(self.xlength):
            for k in range(self.ylength):
                # 计算当前网格点相对于纤芯顶点的位置
                x_index = int(x_center + j - self.xlength // 2)
                y_index = int(y_center + k - self.ylength // 2)

                # 纤芯
                if (x_index - x1) ** 2 + (y_index - y1) ** 2 <= actual_r_LP01 ** 2:
                    permittivity[j, k, :] = n_LP01 ** 2
                elif (x_index - x2) ** 2 + (y_index - y2) ** 2 <= actual_r_LP11a ** 2:
                    permittivity[j, k, :] = n_LP11a ** 2
                elif (x_index - x3) ** 2 + (y_index - y3) ** 2 <= actual_r_LP11b ** 2:
                    permittivity[j, k, :] = n_LP11b ** 2
                elif (x_index - x4) ** 2 + (y_index - y4) ** 2 <= actual_r_LP21a ** 2:
                    permittivity[j, k, :] = n_LP21a ** 2
                elif (x_index - x5) ** 2 + (y_index - y5) ** 2 <= actual_r_LP21b ** 2:
                    permittivity[j, k, :] = n_LP21b ** 2
                elif (x_index - x6) ** 2 + (y_index - y6) ** 2 <= actual_r_LP02 ** 2:
                    permittivity[j, k, :] = n_LP02 ** 2

        return permittivity

    def _compute_priority(self):
        # 初始化优先级矩阵
        self.priority_matrix = np.zeros((self.xlength, self.ylength, self.zlength))
        # 根据每个折射率设置对应的优先级
        for idx, ref_index in enumerate(self.refractive_index):
            self.priority_matrix[self.permittivity == ref_index ** 2] = self.priority[idx]
