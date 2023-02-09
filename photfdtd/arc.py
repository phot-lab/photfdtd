import numpy as np
from .waveguide import Waveguide


class Arc(Waveguide):

    # TODO: 由于在设置的波导中，非波导部分折射率都为1，因此目前设置空间折射率来改变包层折射率并无意义
    """四分之一圆环
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 位置坐标（通常是矩形区域最靠近原点的点）
    width: 波导宽度
    refractive_index:折射率
    name: 名称
    direction: 等于1，2，3，4，分别表征四个方向：左下，左上，右下，右上
    """

    def __init__(
        self,
        outer_radius: int,
        zlength: int,
        x: int,
        y: int,
        z: int,
        width: int,
        refractive_index: float,
        name: str,
        direction: int,
    ) -> None:

        self.direction = direction
        self.outer_radius = outer_radius
        super().__init__(outer_radius, outer_radius, zlength, x, y, z, width, name, refractive_index)

    def _compute_permittivity(self):
        x = y = np.linspace(1, self.outer_radius, self.outer_radius)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要

        if self.direction == 1:
            # direction=1, 圆心在左下
            m = (X - self.outer_radius) ** 2 + Y**2 >= (self.outer_radius - self.width) ** 2
            m1 = (X - self.outer_radius) ** 2 + Y**2 <= self.outer_radius**2

        elif self.direction == 2:
            # direction=2, 圆心在左上
            m = X**2 + Y**2 >= (self.outer_radius - self.width) ** 2
            m1 = X**2 + Y**2 <= self.outer_radius**2

        elif self.direction == 3:
            # direction=3, 圆心在右上
            m = X**2 + (Y - self.outer_radius) ** 2 >= (self.outer_radius - self.width) ** 2
            m1 = X**2 + (Y - self.outer_radius) ** 2 <= self.outer_radius**2

        elif self.direction == 4:
            # direction=4, 圆心在右下
            m = (X - self.outer_radius) ** 2 + (Y - self.outer_radius) ** 2 >= (self.outer_radius - self.width) ** 2
            m1 = (X - self.outer_radius) ** 2 + (Y - self.outer_radius) ** 2 <= self.outer_radius**2

        for i in range(self.outer_radius):
            for j in range(self.outer_radius):
                if m1[i, j] != m[i, j]:
                    m[i, j] = 0

        self.permittivity = np.ones((self.outer_radius, self.outer_radius, self.zlength))
        self.permittivity += m[:, :, None] * (self.refractive_index**2 - 1)
