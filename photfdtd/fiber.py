import numpy as np
from .waveguide import Waveguide


class Circle(Waveguide):
    def __init__(self, length: int or float = 100,
                 x: int or float = None, y: int or float = None, z: int or float = None,
                 radius: int or float = None,
                 refractive_index: int or float = None,
                 name: str = "fiber",
                 axis: str = "z",
                 grid=None,
                 priority: int = 1) -> None:

        length, x, y, z, radius = grid._handle_unit([length, x, y, z, radius], grid_spacing=grid._grid.grid_spacing)
        self.radius = radius
        self.length = length
        self.axis = axis

        if self.axis.lower() == 'x':
            # 波导沿x轴
            xlength = self.length
            ylength = self.radius * 2
            zlength = ylength

        elif self.axis.lower() == 'y':
            # 波导沿y轴
            xlength = self.radius * 2
            ylength = self.length
            zlength = ylength

        elif self.axis.lower() == "z":
            # 波导沿z轴
            ylength = self.radius * 2
            xlength = ylength
            zlength = self.length
        super().__init__(xlength, ylength, zlength, x, y, z, 1, name, refractive_index, grid=grid, priority=priority)

    def _compute_permittivity(self):

        # 这里+2的原因：稍微扩大一点矩阵的大小，可以保证水平和竖直方向最边上的点不被丢出
        # TODO: 给其他带圆弧的波导相同的操作？
        x = y = np.linspace(1, 2 * self.radius + 2, 2 * self.radius + 2)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
        # m = (X - len(x) / 2) ** 2 + (Y - len(y) / 2) ** 2 <= self.radius[0] ** 2
        matrix = np.zeros((len(x), len(y)), dtype=float)

        if self.axis.lower() == 'x':
            # 波导沿x轴
            self.xlength = self.length
            self.ylength = 2 * self.radius + 2
            self.zlength = 2 * self.radius + 2
            self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))

            mask = (X - self.ylength // 2) ** 2 + (Y - self.ylength // 2) ** 2 <= self.radius ** 2
            matrix[mask] = 1

            matrix[matrix == 1] = self.refractive_index ** 2
            matrix[matrix == 0] = self.background_index ** 2

            self.permittivity = matrix

        elif self.axis.lower() == 'y':
            # 波导沿y轴
            self.xlength = 2 * self.radius + 2
            self.ylength = self.length
            self.zlength = 2 * self.radius + 2
            self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))

            mask = (X - self.xlength // 2) ** 2 + (Y - self.xlength // 2) ** 2 <= self.radius ** 2
            matrix[mask] = 1

            matrix[matrix == 1] = self.refractive_index ** 2
            matrix[matrix == 0] = self.background_index ** 2

            self.permittivity[:, 0] = matrix

        elif self.axis.lower() == 'z':
            # 波导沿z轴
            self.xlength = 2 * self.radius + 2
            self.ylength = 2 * self.radius + 2
            self.zlength = self.length
            self.permittivity = np.zeros((self.xlength, self.ylength, self.zlength))

            mask = (X - self.ylength // 2) ** 2 + (Y - self.ylength // 2) ** 2 <= self.radius ** 2
            matrix[mask] = 1

            matrix[matrix == 1] = self.refractive_index ** 2
            matrix[matrix == 0] = self.background_index ** 2

            self.permittivity[:, :, 0] = matrix




class Fiber(Circle):
    """光纤
    radius: list，表示从里到外每一层的半径
    refractive_index: list，表示从里到外每一层的折射率
    length: 长度
    x,y,z: 位置坐标（中心）
    name: 名称
    axis: 'x', 'y', "z" 光纤沿哪个轴
    background_index：背景折射率
    priority: the priority of the waveguide( high index indicates high priority).
    """

    # TODO: 渐变折射率光纤
    def __init__(self, length: int or float = 100, x: int or float = None, y: int or float = None,
                 z: int or float = None,
                 radius: list = [10, 40],
                 refractive_index: list = [3.47, 1.45],
                 name: str = "fiber", axis: str = "z",
                 grid=None,
                 priority: int = 1) -> None:
        if len(radius) != len(refractive_index):
            raise ValueError("Radius'length does not match the length of refractive_index")
        self.length, self.x, self.y, self.z, self.radius, self.refractive_index, self.name, self.axis, self.grid, self.priority = \
        length, x, y, z, radius, refractive_index, name, axis, grid, priority
        if self.axis.lower() == 'x':
            # 波导沿x轴
            self.xlength = self.length
            self.ylength = self.radius[-1] * 2
            self.zlength = self.ylength

        elif self.axis.lower() == 'y':
            # 波导沿y轴
            self.xlength = self.radius[-1] * 2
            self.ylength = self.length
            self.zlength = self.ylength

        elif self.axis.lower() == "z":
            # 波导沿z轴
            self.ylength = self.radius[-1] * 2
            self.xlength = self.ylength
            self.zlength = self.length
        self._set_objects()
        # length, x, y, z = grid._handle_unit([length, x, y, z], grid_spacing=grid._grid.grid_spacing)
        # radius = grid._handle_unit(radius, grid_spacing=grid._grid.grid_spacing)
        # self.radius = radius
        # self.length = length
        # self.axis = axis
        # if x == None:
        #     # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
        #     x = int(grid._grid_xlength / 2)
        # if y == None:
        #     y = int(grid._grid_ylength / 2)
        # if z == None:
        #     z = int(grid._grid_zlength / 2)
        #
        # if self.axis.lower() == 'x':
        #     # 波导沿x轴
        #     self.x = int(x - self.length // 2)
        #     self.y = int(y - self.radius[-1])
        #     self.z = int(z - self.radius[-1])
        #
        # elif self.axis.lower() == 'y':
        #     # 波导沿y轴
        #     self.y = int(y - self.length // 2)
        #     self.x = int(x - self.radius[-1])
        #     self.z = int(z - self.radius[-1])
        #
        # elif self.axis.lower() == "z":
        #     # 波导沿z轴
        #     self.z = int(z - self.length // 2)
        #     self.x = int(x - self.radius[-1])
        #     self.y = int(y - self.radius[-1])
        #
        # self.name = name
        # self.refractive_index = refractive_index
        # self.background_index = grid.background_index
        #
        # # save the center position保存中心
        # self.x_center = x
        # self.y_center = y
        # self.z_center = z
        #
        # self._compute_permittivity()
        # self._set_objects()
        #
        # self.priority = priority
        # super()._compute_priority()

    def _set_objects(self):
        self._internal_objects = []
        for i in range(len(self.radius)):
            fiber = Circle(length=self.length, x=self.x, y=self.y, z=self.z, radius=self.radius[-i], refractive_index=self.refractive_index[-i],
                           name="%s_%i" % (self.name, len(self.radius) - i), axis=self.axis, grid=self.grid, priority=self.priority)
            self._internal_objects.append(fiber)