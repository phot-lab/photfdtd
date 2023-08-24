from .waveguide import Waveguide
import numpy as np


class Ring(Waveguide):
    # TODO: 由于在设置的波导中，非波导部分折射率都为1，因此目前设置空间折射率来改变包层折射率并无意义
    """环形谐振腔，继承自Waveguide
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 位置坐标（通常是矩形区域最靠近原点的点）
    width: 波导宽度
    length: 耦合长度
    gap: 环与直波导间距
    refractive_index:折射率
    name: 名称
    direction: 方向
    """

    def __init__(
        self,
        outer_radius: int = 60,
        zlength: int = 10,
        x: int = 50,
        y: int = 50,
        z: int = 50,
        width: int = 5,
        length: int = 0,
        gap: int = 0,
        name: str = "ring",
        refractive_index: float = 3.47,
        direction: int = 1,
    ):
        self.outer_r = outer_radius
        self.length = length
        self.gap = gap
        self.direction = direction
        xlength = self.outer_r * 2 + self.length
        ylength = self.outer_r * 2

        super().__init__(
            xlength, ylength, zlength, x, y, z, width, name, refractive_index
        )

        self.y = self.y + self.width + self.gap

    def _compute_permittivity(self):
        y = np.linspace(1, 2 * self.outer_r, 2 * self.outer_r)
        x = np.linspace(
            1, 2 * self.outer_r + self.length, 2 * self.outer_r + self.length
        )
        # TODO: 把这个语句改成从1开始？
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要

        if self.length == 0:
            m1 = (self.outer_r - self.width) ** 2 <= (X - self.outer_r) ** 2 + (
                Y - self.outer_r
            ) ** 2
            m = (X - self.outer_r) ** 2 + (Y - self.outer_r) ** 2 <= self.outer_r**2

        for i in range(2 * self.outer_r + self.length):
            for j in range(2 * self.outer_r):
                if m[i, j] != m1[i, j]:
                    m[i, j] = 0

        else:
            m = np.zeros(
                (self.outer_r * 2 + self.length, self.outer_r * 2, self.zlength)
            )

            for j in range(2 * self.outer_r):
                for i in range(self.outer_r):
                    # 左半圆弧
                    if (self.outer_r - self.width) ** 2 <= (
                        X[i, j] - self.outer_r
                    ) ** 2 + (Y[i, j] - self.outer_r) ** 2 and (
                        X[i, j] - self.outer_r
                    ) ** 2 + (
                        Y[i, j] - self.outer_r
                    ) ** 2 <= self.outer_r**2:
                        m[i, j] = 1

                    if (self.outer_r - self.width) ** 2 <= (
                        X[self.outer_r + self.length + i, j]
                        - self.outer_r
                        - self.length
                    ) ** 2 + (
                        Y[self.outer_r + self.length + i, j] - self.outer_r
                    ) ** 2 and (
                        X[self.outer_r + self.length + i, j]
                        - self.outer_r
                        - self.length
                    ) ** 2 + (
                        Y[self.outer_r + self.length + i, j] - self.outer_r
                    ) ** 2 <= self.outer_r**2:
                        m[self.outer_r + self.length + i, j] = 1

            for i in range(self.length):
                for j in range(self.width):
                    # 直波导
                    m[i + self.outer_r, j] = m1[i + self.outer_r, j] = 1
                    m[i + self.outer_r, 2 * self.outer_r - j - 1] = m1[
                        i + self.outer_r, 2 * self.outer_r - j - 1
                    ] = 1

        permittivity = np.ones(
            (self.outer_r * 2 + self.length, self.outer_r * 2, self.zlength)
        )
        permittivity += m[:, :] * (self.refractive_index**2 - 1)

        self.permittivity = permittivity

    def _set_objects(self):
        wg_bottom = Waveguide(
            xlength=self.outer_r * 2 + self.length,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            width=self.width,
            name=f"waveguide_bottom_{self.name}",
            refractive_index=self.refractive_index,
        )

        wg_top = Waveguide(
            xlength=self.outer_r * 2 + self.length,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y + self.width + self.gap * 2 + self.outer_r * 2,
            z=self.z,
            width=self.width,
            name=f"waveguide_top_{self.name}",
            refractive_index=self.refractive_index,
        )

        self._internal_objects = [self, wg_top, wg_bottom]
