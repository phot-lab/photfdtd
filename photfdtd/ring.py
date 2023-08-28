from .waveguide import Waveguide
import numpy as np


class Ring(Waveguide):
    """环形谐振腔，继承自Waveguide
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 环中心坐标
    width: 波导宽度
    length: 耦合长度
    gap: 环与直波导间距
    refractive_index:折射率
    name: 名称
    direction: 方向
    """

    def __init__(
        self,
        outer_radius=100,
        zlength=20,
        x=150,
        y=150,
        z=13,
        width=20,
        length=0,
        gap=5,
        name="ring",
        refractive_index=3.47,
        direction=1,
        background_index: float = 1
    ):

        self.outer_r = outer_radius
        self.length = length
        self.gap = gap
        self.direction = direction
        xlength = self.outer_r * 2 + self.length
        ylength = self.outer_r * 2

        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, background_index)



    def _compute_permittivity(self):
        y = np.linspace(1, 2 * self.outer_r, 2 * self.outer_r)
        x = np.linspace(1, 2 * self.outer_r + self.length, 2 * self.outer_r + self.length)
        # TODO: 把这个语句改成从1开始？
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要

        if self.length == 0:

            m1 = (self.outer_r - self.width) ** 2 <= (X - self.outer_r) ** 2 + (Y - self.outer_r) ** 2
            m = (X - self.outer_r) ** 2 + (Y - self.outer_r) ** 2 <= self.outer_r**2

        for i in range(2 * self.outer_r + self.length):
            for j in range(2 * self.outer_r):
                if m[i, j] != m1[i, j]:
                    m[i, j] = 0

        else:

            m = np.zeros((self.outer_r * 2 + self.length, self.outer_r * 2, self.zlength))

            for j in range(2 * self.outer_r):
                for i in range(self.outer_r):

                    # 左半圆弧
                    if (self.outer_r - self.width) ** 2 <= (X[i, j] - self.outer_r) ** 2 + (
                        Y[i, j] - self.outer_r
                    ) ** 2 and (X[i, j] - self.outer_r) ** 2 + (Y[i, j] - self.outer_r) ** 2 <= self.outer_r**2:
                        m[i, j] = 1

                    if (self.outer_r - self.width) ** 2 <= (
                        X[self.outer_r + self.length + i, j] - self.outer_r - self.length
                    ) ** 2 + (Y[self.outer_r + self.length + i, j] - self.outer_r) ** 2 and (
                        X[self.outer_r + self.length + i, j] - self.outer_r - self.length
                    ) ** 2 + (
                        Y[self.outer_r + self.length + i, j] - self.outer_r
                    ) ** 2 <= self.outer_r**2:
                        m[self.outer_r + self.length + i, j] = 1

            for i in range(self.length):
                for j in range(self.width):
                    # 直波导
                    m[i + self.outer_r, j] = m1[i + self.outer_r, j] = 1
                    m[i + self.outer_r, 2 * self.outer_r - j - 1] = m1[i + self.outer_r, 2 * self.outer_r - j - 1] = 1

        permittivity = np.ones((self.outer_r * 2 + self.length, self.outer_r * 2, self.zlength))
        permittivity += m[:, :] * (self.refractive_index**2 - 1)
        permittivity += (1 - m[:, :]) * (self.background_index ** 2 - 1)

        self.permittivity = permittivity

    def _set_objects(self):

        self.x = self.x + int(self.xlength / 2)
        self.y = self.y + int(self.ylength / 2)
        self.z = self.z + int(self.zlength / 2)

        wg_bottom = Waveguide(
            xlength=self.outer_r * 2 + self.length,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y - self.outer_r - self.gap - int(self.width / 2),
            z=self.z,
            width=self.width,
            name="waveguide_bottom_%s" % self.name,
            refractive_index=self.refractive_index,
            background_index=self.background_index
        )

        wg_top = Waveguide(
            xlength=self.outer_r * 2 + self.length,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y + self.outer_r + self.gap + int(self.width / 2),
            z=self.z,
            width=self.width,
            name="waveguide_top_%s" % self.name,
            refractive_index=self.refractive_index,
            background_index=self.background_index
        )

        self.x = self.x - int(self.xlength / 2)
        self.y = self.y - int(self.ylength / 2)
        self.z = self.z - int(self.zlength / 2)

        self._internal_objects = [self, wg_top, wg_bottom]
