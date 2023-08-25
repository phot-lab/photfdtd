import numpy as np
from .waveguide import Waveguide


class Fiber(Waveguide):
    """光纤
    radius: 半径
    length: 长度
    x,y,z: 位置坐标（中心）
    refractive_index:折射率
    name: 名称
    axis: 'x', 'y', 'z' 波导沿哪个轴
    """

    # TODO: 多芯光纤、渐变折射率光纤
    def __init__(self,
                 length: int, x: int, y: int, z: int,
                 radius: list = [],
                 refractive_index: list = [],
                 name: str = "",
                 axis: str = "x",
                 background_index: float = 1,

                 ) -> None:

        self.radius = radius
        self.length = length
        self.axis = axis
        if self.axis.lower() == 'x':
            # 23.08
            # 波导沿x轴

            self.x = x - self.length // 2
            self.y = y - self.radius[-1]
            self.z = z - self.radius[-1]

        elif self.axis.lower() == 'y':
            # 波导沿y轴
            self.y = y - self.length // 2
            self.x = x - self.radius[-1]
            self.z = z - self.radius[-1]

        self.name = name
        self.refractive_index = refractive_index
        self.background_index = background_index

        self._compute_permittivity()
        self._set_objects()

    def _compute_permittivity(self):

        # 这里+2的原因：稍微扩大一点矩阵的大小，可以保证水平和竖直方向最边上的点不被丢出
        # TODO: 给其他带圆弧的波导相同的操作？
        x = y = np.linspace(1, 2 * self.radius[-1] + 2, 2 * self.radius[-1] + 2)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
        # m = (X - len(x) / 2) ** 2 + (Y - len(y) / 2) ** 2 <= self.radius[0] ** 2
        matrix = np.zeros((len(x), len(y)), dtype=float)

        if self.axis.lower() == 'x':
            # 波导沿x轴
            self.xlength = self.length
            self.ylength = 2 * self.radius[-1] + 2
            self.zlength = 2 * self.radius[-1] + 2
            self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))

            for i in range(len(self.radius)):
                i = len(self.radius) - i - 1
                mask = (X - self.ylength // 2) ** 2 + (Y - self.ylength // 2) ** 2 <= self.radius[i] ** 2
                matrix[mask] = i + 1

            for i in range(self.length):
                for j in range(len(self.refractive_index)):
                    matrix[matrix == j + 1] = self.refractive_index[j] ** 2
                    matrix[matrix == 0] = self.background_index ** 2
                self.permittivity[i] = matrix

        elif self.axis.lower() == 'y':
            # 波导沿x轴
            self.xlength = 2 * self.radius[-1] + 2
            self.ylength = self.length
            self.zlength = 2 * self.radius[-1] + 2
            self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))

            for i in range(len(self.radius)):
                i = len(self.radius) - i - 1
                mask = (X - self.xlength // 2) ** 2 + (Y - self.xlength // 2) ** 2 <= self.radius[i] ** 2
                matrix[mask] = i + 1

            for i in range(self.length):
                for j in range(len(self.refractive_index)):
                    matrix[matrix == j + 1] = self.refractive_index[j] ** 2
                    matrix[matrix == 0] = self.background_index ** 2
                self.permittivity[:, i] = matrix
            print()
        # elif self.axis.lower() == 'y':
        #     # 波导沿y轴
        #     self.xlength = 2*self.radius+2
        #     self.ylength = self.length
        #     self.zlength = 2*self.radius+2
        #     self.permittivity = np.ones((2*self.radius+2, self.length, 2*self.radius+2))
        #     for i in range(self.length):
        #         self.permittivity[:, i] += m[:, :] * (self.refractive_index ** 2 - 1)
        #         self.permittivity[:, i] += (1 - m[:, :]) * (self.background_index ** 2 - 1)
        #
        # elif self.axis.lower() == 'z':
        #     # 波导沿z轴
        #     self.xlength = 2*self.radius+2
        #     self.ylength = 2*self.radius+2
        #     self.zlength = self.length
        #     self.permittivity = np.ones((2*self.radius+2, 2*self.radius+2, self.length))
        #     for i in range(self.length):
        #         self.permittivity[:, :, i] += m[:, :] * (self.refractive_index ** 2 - 1)
        #         self.permittivity[:, :, i] += (1 - m[:, :]) * (self.background_index ** 2 - 1)

    def _set_objects(self):
        self._internal_objects = [self]
