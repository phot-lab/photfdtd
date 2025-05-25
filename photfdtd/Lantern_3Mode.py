import numpy as np
from photfdtd import Waveguide

class Lantern_3Mode(Waveguide):
    """
    三模光子灯笼
    x, y, z: 中心坐标
    distance：纤芯距离
    r_LP01:纤芯1半径
    r_LP11a:纤芯2半径
    r_LP11b:纤芯3半径
    n_LP01:纤芯1折射率
    n_LP11a:纤芯2折射率
    n_LP11b:纤芯3折射率
    n_cladding:包层折射率
    r_cladding:包层半径
    taper_ratio:拉锥比
    """

    def __init__(self, grid,  x: int or float = None,
                 y: int or float = None,
                 z: int or float = None,length: int or float = 100, distance: int or float = 50e-6,
                 r_LP01=100e-6, r_LP11a=100e-6, r_LP11b=100e-6,
                 n_LP01=1.45, n_LP11a=1.46, n_LP11b=1.47, n_cladding=1.44, r_cladding=62.5e-6,
                 taper_ratio=0.1, name="lantern_3mode", axis="z", priority=[1, 1, 1, 1]):
        # 自动选择仿真区域中心
        self.x = x if x is not None else int(grid._grid_xlength / 2)
        self.y = y if y is not None else int(grid._grid_ylength / 2)
        self.z = z if z is not None else int(grid._grid_zlength / 2)
        # 处理输入参数的单位统一化
        length, _, _, _ = grid._handle_unit([length, 0, 0, 0], grid_spacing=grid._grid.grid_spacing)
        distance = grid._handle_unit([distance], grid_spacing=grid._grid.grid_spacing)[0]
        r_LP01, r_LP11a, r_LP11b, r_cladding = grid._handle_unit([r_LP01, r_LP11a, r_LP11b, r_cladding], grid_spacing=grid._grid.grid_spacing)

        # 定义 background_index 属性
        self.background_index = 1.4398
        # 定义_internal_objects属性
        self._internal_objects = [self]

        # 计算各纤芯位置的实际坐标
        actual_distance = distance * taper_ratio#实际的纤芯距离
        x1 =int(self.x)
        y1 = int(self.y + actual_distance / np.sqrt(3))
        x2 = int(self.x - actual_distance / 2)
        y2 = int(self.y - actual_distance/np.sqrt(3) /2)
        x3 = int(self.x + actual_distance / 2)
        y3 = int(self.y - actual_distance/np.sqrt(3) / 2)
        # 计算实际上的纤芯半径和包层半径
        actual_r_LP01 = r_LP01 * taper_ratio
        actual_r_LP11a = r_LP11a * taper_ratio
        actual_r_LP11b = r_LP11b * taper_ratio
        actual_r_cladding = r_cladding * taper_ratio

        # 初始化 xlength、ylength 和 zlength 属性
        self.xlength = int(2 * actual_r_cladding)
        self.ylength = int(2 * actual_r_cladding)
        self.zlength = length



        # 计算介电常数矩阵
        permittivity = self.compute_permittivity(grid, length, self.x, self.y, x1, y1, x2, y2, x3, y3,
                                                  actual_r_LP01, actual_r_LP11a, actual_r_LP11b, actual_r_cladding,
                                                  n_LP01, n_LP11a, n_LP11b, n_cladding)

        # 保存属性值
        self.permittivity = permittivity
        self.priority = priority
        self.n_cladding = n_cladding
        self.name = name
        self.length = length
        self.axis = axis
        self.priority = priority
        self.refractive_index = [n_LP01, n_LP11a, n_LP11b, n_cladding]
        # 初始化其他属性
        self.x = int(grid._grid_xlength / 2 - actual_r_cladding)
        self.y = int(grid._grid_ylength / 2 - actual_r_cladding)
        self.z = int(grid._grid_zlength / 2 - length / 2)



        # 计算优先级矩阵
        self._compute_priority()

    def compute_permittivity(self, grid, length, x_center, y_center, x1, y1, x2, y2, x3, y3, actual_r_LP01,
                         actual_r_LP11a, actual_r_LP11b, actual_r_cladding, n_LP01, n_LP11a, n_LP11b, n_cladding):
        # 初始化介电常数矩阵
        #permittivity = np.full((self.xlength, self.ylength, self.zlength), self.background_index ** 2)
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
                # 计算光子灯笼对象在仿真区域中的位置
                x_index = int(x_center + j - self.xlength // 2)
                y_index = int(y_center + k - self.ylength // 2)

                # 纤芯
                if (x_index - x1) ** 2 + (y_index - y1) ** 2 <= actual_r_LP01 ** 2:
                    permittivity[j, k, :] = n_LP01 ** 2
                elif (x_index - x2) ** 2 + (y_index - y2) ** 2 <= actual_r_LP11a ** 2:
                    permittivity[j, k, :] = n_LP11a ** 2
                elif (x_index - x3) ** 2 + (y_index - y3) ** 2 <= actual_r_LP11b ** 2:
                    permittivity[j, k, :] = n_LP11b ** 2

        return permittivity

    def _compute_priority(self):
        # 初始化优先级矩阵
        self.priority_matrix = np.zeros((self.xlength, self.ylength, self.zlength))
        # 根据每个折射率设置对应的优先级
        for idx, ref_index in enumerate(self.refractive_index):
            self.priority_matrix[self.permittivity == ref_index ** 2] = self.priority[idx]
