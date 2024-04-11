import numpy as np
from .waveguide import Waveguide


class Ellipsoid(Waveguide):
    """椭圆形（光纤）
    a: int or float，long semi-axis
    b: int or float, short semi-axis
    refractive_index: n
    length: 长度
    x,y,z: 位置坐标（中心）
    name: 名称
    axis: 'x', 'y', "z" 光纤沿哪个轴
    """

    def __init__(self, length: int or float = None, x: int or float = None, y: int or float = None,
                 z: int or float = None,
                 a: int or float = None, b: int or float = None,
                 refractive_index: float = None,
                 name: str = "ellipsoid", axis: str = "z",
                 grid=None) -> None:
        length, x, y, z, a, b = grid._handle_unit([length, x, y, z, a, b], grid_spacing=grid._grid.grid_spacing)
        self.a = a
        self.b = b
        self.radius = max(a, b)
        self.length = length
        self.axis = axis
        if x == None:
            # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
            x = int(grid._grid_xlength / 2)
        if y == None:
            y = int(grid._grid_ylength / 2)
        if z == None:
            z = int(grid._grid_zlength / 2)

        if self.axis.lower() == 'x':
            # 波导沿x轴
            self.x = int(x - self.length // 2)
            self.y = int(y - self.radius)
            self.z = int(z - self.radius)

        elif self.axis.lower() == 'y':
            # 波导沿y轴
            self.y = int(y - self.length // 2)
            self.x = int(x - self.radius)
            self.z = int(z - self.radius)

        elif self.axis.lower() == "z":
            # 波导沿z轴
            self.z = int(z - self.length // 2)
            self.x = int(x - self.radius)
            self.y = int(y - self.radius)

        self.name = name
        self.refractive_index = refractive_index
        self.background_index = grid.background_index

        # save the center position保存中心
        self.x_center = x
        self.y_center = y
        self.z_center = z

        self._compute_permittivity()
        self._set_objects()

    def _plot_(self):
        pass

    def _compute_permittivity(self):

        # 这里+2的原因：稍微扩大一点矩阵的大小，可以保证水平和竖直方向最边上的点不被丢出
        # TODO: 给其他带圆弧的波导相同的操作？
        x = y = np.linspace(1, 2 * self.radius + 2, 2 * self.radius + 2)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
        # m = (X - len(x) / 2) ** 2 + (Y - len(y) / 2) ** 2 <= self.radius[0] ** 2
        matrix = np.zeros((len(x), len(y)), dtype=float)
        # self.xlength = 2 * self.radius + 2
        # self.ylength = 2 * self.radius + 2
        # self.zlength = self.length
        self.permittivity = np.zeros((2 * self.radius + 2, 2 * self.radius + 2, self.length))

        mask = ((X - self.permittivity.shape[0] // 2) / self.a) ** 2 + ((Y - self.permittivity.shape[1] // 2) / self.b) ** 2 <= 1
        matrix[mask] = self.refractive_index ** 2

        matrix[matrix == 0] = self.background_index ** 2

        for i in range(self.length):
            self.permittivity[:, :, i] = matrix

        if self.axis.lower() == 'x':
            # 波导沿x轴
            self.permittivity = np.transpose(self.permittivity, axes=(2, 0, 1))

            # self.xlength = self.length
            # self.ylength = 2 * self.radius[-1] + 2
            # self.zlength = 2 * self.radius[-1] + 2
            # self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
            #
            # for i in range(len(self.radius)):
            #     i = len(self.radius) - i - 1
            #     mask = (X - self.ylength // 2) ** 2 + (Y - self.ylength // 2) ** 2 <= self.radius[i] ** 2
            #     matrix[mask] = i + 1
            #
            # for j in range(len(self.refractive_index)):
            #     matrix[matrix == j + 1] = self.refractive_index[j] ** 2
            #     matrix[matrix == 0] = self.background_index ** 2
            #
            # for i in range(self.length):
            #     self.permittivity[i] = matrix

        elif self.axis.lower() == 'y':
            # 波导沿y轴
            self.permittivity = np.transpose(self.permittivity, axes=(0, 2, 1))
            # self.xlength = 2 * self.radius[-1] + 2
            # self.ylength = self.length
            # self.zlength = 2 * self.radius[-1] + 2
            # self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
            #
            # for i in range(len(self.radius)):
            #     i = len(self.radius) - i - 1
            #     mask = (X - self.xlength // 2) ** 2 + (Y - self.xlength // 2) ** 2 <= self.radius[i] ** 2
            #     matrix[mask] = i + 1
            #
            # for j in range(len(self.refractive_index)):
            #     matrix[matrix == j + 1] = self.refractive_index[j] ** 2
            #     matrix[matrix == 0] = self.background_index ** 2
            #
            # for i in range(self.length):
            #     self.permittivity[:, i] = matrix

        self.xlength = self.permittivity.shape[0]
        self.ylength = self.permittivity.shape[1]
        self.zlength = self.permittivity.shape[2]

