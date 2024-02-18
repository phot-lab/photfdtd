from .waveguide import Waveguide
from .arc import Arc
import numpy as np


class Ring(Waveguide):
    """环形谐振腔，继承自Waveguide
    outer_radius: 外环半径
    ylength: 波导厚度
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
            outer_radius: int or float = 100,
            ylength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width: int or float = 20,
            length: int or float = 0,
            gap: int or float = 5,
            name: str = "ring",
            refractive_index: float = 3.47,
            direction: int = 1,
            grid=None
    ) -> None:
        outer_radius, ylength, width, length, gap = grid._handle_unit([outer_radius, ylength, width, length, gap],
                                                                      grid_spacing=grid._grid.grid_spacing)
        self.outer_r = outer_radius
        self.length = length
        self.gap = gap
        self.direction = direction
        zlength = self.outer_r * 2 + self.length
        xlength = self.outer_r * 2

        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, grid=grid, reset_xyz=False)

    def _compute_permittivity(self):
        # y = np.linspace(1, 2 * self.outer_r, 2 * self.outer_r)
        # z = np.linspace(1, 2 * self.outer_r + self.length, 2 * self.outer_r + self.length)
        # # TODO: 把这个语句改成从1开始？
        # Z, Y = np.meshgrid(z, y, indexing="ij")  # indexing = 'ij'很重要
        #

        delta_z = int(np.round(self.length / 2))
        arc1 = Arc(outer_radius=self.outer_r, ylength=self.ylength, width=self.width,
                   x=self.x, y=self.y,z=self.z - delta_z,refractive_index=self.refractive_index,
                   name="%s_arc1" % self.name, angle_phi=90, angle_psi=180, grid=self.grid)
        arc2 = Arc(outer_radius=self.outer_r, ylength=self.ylength, width=self.width,
                   x=self.x, y=self.y, z=self.z + delta_z, refractive_index=self.refractive_index,
                   name="%s_arc3" % self.name, angle_phi=270, angle_psi=180, grid=self.grid)
        self._internal_objects = [arc1, arc2]
        if self.length > 0:
            wg3 = Waveguide(
                xlength=self.width,
                ylength=self.ylength,
                zlength=self.length,
                x=self.x - self.outer_r + int(self.width / 2),
                y=self.y,
                z=self.z,
                width=self.width,
                name="%s_waveguide3" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid
            )

            wg4 = Waveguide(
                xlength=self.width,
                ylength=self.ylength,
                zlength=self.length,
                x=self.x + self.outer_r - int(self.width / 2),
                y=self.y,
                z=self.z,
                width=self.width,
                name="%s_waveguide4" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid
            )
            self._internal_objects += [wg3, wg4]

        #     m1 = (self.outer_r - self.width) ** 2 <= (Z - self.outer_r) ** 2 + (Y - self.outer_r) ** 2
        #     m = (Z - self.outer_r) ** 2 + (Y - self.outer_r) ** 2 <= self.outer_r ** 2
        #
        # for i in range(2 * self.outer_r + self.length):
        #     for j in range(2 * self.outer_r):
        #         if m[i, j] != m1[i, j]:
        #             m[i, j] = 0
        #
        # else:
        #
        #     m = np.zeros((self.outer_r * 2, self.zlength, self.outer_r * 2 + self.length))
        #
        #     for j in range(2 * self.outer_r):
        #         for i in range(self.outer_r):
        #
        #             # 左半圆弧
        #             if (self.outer_r - self.width) ** 2 <= (X[i, j] - self.outer_r) ** 2 + (
        #                     Y[i, j] - self.outer_r
        #             ) ** 2 and (X[i, j] - self.outer_r) ** 2 + (Y[i, j] - self.outer_r) ** 2 <= self.outer_r ** 2:
        #                 m[i, j] = 1
        #
        #             if (self.outer_r - self.width) ** 2 <= (
        #                     X[self.outer_r + self.length + i, j] - self.outer_r - self.length
        #             ) ** 2 + (Y[self.outer_r + self.length + i, j] - self.outer_r) ** 2 and (
        #                     X[self.outer_r + self.length + i, j] - self.outer_r - self.length
        #             ) ** 2 + (
        #                     Y[self.outer_r + self.length + i, j] - self.outer_r
        #             ) ** 2 <= self.outer_r ** 2:
        #                 m[self.outer_r + self.length + i, j] = 1
        #
        #     for i in range(self.length):
        #         for j in range(self.width):
        #             # 直波导
        #             m[i + self.outer_r, j] = m1[i + self.outer_r, j] = 1
        #             m[i + self.outer_r, 2 * self.outer_r - j - 1] = m1[i + self.outer_r, 2 * self.outer_r - j - 1] = 1
        #



    def _set_objects(self):

        wg_bottom = Waveguide(
            xlength=self.width,
            ylength=self.ylength,
            zlength=self.outer_r * 2 + self.length,
            x=self.x - self.outer_r - self.gap - int(self.width / 2),
            y=self.y,
            z=self.z,
            width=self.width,
            name="%s_waveguide1" % self.name,
            refractive_index=self.refractive_index,
            grid=self.grid
        )

        wg_top = Waveguide(
            xlength=self.width,
            ylength=self.ylength,
            zlength=self.outer_r * 2 + self.length,
            x=self.x + self.outer_r + self.gap + int(self.width / 2),
            y=self.y,
            z=self.z,
            width=self.width,
            name="%s_waveguide2" % self.name,
            refractive_index=self.refractive_index,
            grid=self.grid
        )

        # self.x = self.x - int(self.xlength / 2)
        # self.y = self.y - int(self.ylength / 2)
        # self.z = self.z - int(self.zlength / 2)

        self._internal_objects += [wg_top, wg_bottom]
