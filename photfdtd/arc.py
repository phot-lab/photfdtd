import numpy as np
from .waveguide import Waveguide


class Arc(Waveguide):
    """四分之一圆环
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 位置坐标矩形区域最靠近原点的点（这一点与其他波导不同，如果）
    width: 波导宽度
    refractive_index:折射率
    name: 名称
    direction: 等于1，2，3，4，分别表示四个方向
    background_index: 环境折射率
    """

    def __init__(
        self,
        outer_radius: int = 60,
        zlength: int = 20,
        x: int = 100,
        y: int = 100,
        z: int = 1,
        width: int = 20,
        refractive_index: float = 3.47,
        name: str = "arc",
        direction: int = 1,
        background_index: float = 1
    ) -> None:

        self.direction = direction
        self.outer_radius = outer_radius
        super().__init__(outer_radius, outer_radius, zlength, x + int(outer_radius / 2), y + int(outer_radius / 2), z + int(zlength / 2), width, name, refractive_index, background_index)

    def _compute_permittivity(self):
        x = y = np.linspace(1, self.outer_radius, self.outer_radius)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要

        if self.direction == 1:
            # direction=1, 圆心在(outer_radius,0)
            m = (X - self.outer_radius) ** 2 + Y**2 >= (self.outer_radius - self.width) ** 2
            m1 = (X - self.outer_radius) ** 2 + Y**2 <= self.outer_radius**2

        elif self.direction == 2:
            # direction=2, 圆心在(0, 0)
            m = X**2 + Y**2 >= (self.outer_radius - self.width) ** 2
            m1 = X**2 + Y**2 <= self.outer_radius**2

        elif self.direction == 3:
            # direction=3, 圆心在(0, outer_radius)
            m = X**2 + (Y - self.outer_radius) ** 2 >= (self.outer_radius - self.width) ** 2
            m1 = X**2 + (Y - self.outer_radius) ** 2 <= self.outer_radius**2

        elif self.direction == 4:
            # direction=4, 圆心在(outer_radius, outer_radius)
            m = (X - self.outer_radius) ** 2 + (Y - self.outer_radius) ** 2 >= (self.outer_radius - self.width) ** 2
            m1 = (X - self.outer_radius) ** 2 + (Y - self.outer_radius) ** 2 <= self.outer_radius**2

        for i in range(self.outer_radius):
            for j in range(self.outer_radius):
                if m1[i, j] != m[i, j]:
                    m[i, j] = 0

        self.permittivity = np.ones((self.outer_radius, self.outer_radius, self.zlength))
        self.permittivity += m[:, :, None] * (self.refractive_index**2 - 1)
        self.permittivity += (1 - m[:, :, None]) * (self.background_index ** 2 - 1)
