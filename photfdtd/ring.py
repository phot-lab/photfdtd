from .waveguide import Waveguide
from .arc import Arc
import photfdtd.fdtd.backend as bd


class Ring(Waveguide):
    """
    微环谐振器参数说明 / Ring Resonator Parameters:

    Args:
        outer_radius (float): 外环半径 / Outer radius of the ring
        ylength (float): 波导厚度 / Waveguide thickness (height)
        x, y, z (float): 环中心坐标 / Center coordinates of the ring
        width (float): 波导宽度 / Waveguide width
        length (float): 耦合长度 / Coupling length
        gap (float): 环与直波导间距 / Gap between ring and straight waveguide
        refractive_index (float): 折射率 / Refractive index
        name (str): 名称 / Name identifier
        direction (str): 方向 / Direction
        priority (int): 波导优先级，数值越高优先级越高 / Priority of the waveguide (higher value = higher priority)

    """

    def __init__(
            self,
            outer_radius: int or float = 100,
            ylength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width_s: int or float = 20,
            width_r: int or float = None,
            length_s: int or float = None,
            length: int or float = 0,
            gap: int or float = 5,
            name: str = "ring",
            refractive_index: float = 3.47,
            direction: int = 1,
            grid=None,
            priority: int = 1
    ) -> None:
        if length_s is None:
            length_s = outer_radius * 2 + length
        outer_radius, width_s, width_r, length, gap, length_s = grid._handle_unit(
            [outer_radius, width_s, width_r, length, gap, length_s],
            grid_spacing=grid._grid.grid_spacing)
        ylength = grid._handle_unit([ylength], grid_spacing=grid._grid.grid_spacing_y)[0]
        self.outer_r = outer_radius
        self.length = length
        self.gap = gap
        self.direction = direction
        self.length_s = length_s
        zlength = self.outer_r * 2 + self.length
        xlength = self.outer_r * 2
        if not width_r:
            self.width_r = width_s
        else:
            self.width_r = width_r
        super().__init__(xlength, ylength, zlength, x, y, z, width_s, name, refractive_index, grid=grid,
                         reset_xyz=False, priority=priority)

    def _compute_permittivity(self):
        # y = bd.linspace(1, 2 * self.outer_r, 2 * self.outer_r)
        # z = bd.linspace(1, 2 * self.outer_r + self.length, 2 * self.outer_r + self.length)
        # # TODO: 把这个语句改成从1开始？
        # Z, Y = bd.meshgrid(z, y, indexing="ij")  # indexing = 'ij'很重要
        #

        delta_z = int(bd.round(self.length / 2))

        arc1 = Arc(outer_radius=self.outer_r, ylength=self.ylength, x=self.x, y=self.y, z=self.z + delta_z,
                   width=self.width_r, refractive_index=self.refractive_index, name="%s_arc1" % self.name, angle_phi=0,
                   angle_psi=180, angle_unit=True, grid=self.grid, priority=self.priority)
        arc2 = Arc(outer_radius=self.outer_r, ylength=self.ylength, x=self.x, y=self.y, z=self.z - delta_z,
                   width=self.width_r, refractive_index=self.refractive_index, name="%s_arc2" % self.name,
                   angle_phi=180, angle_psi=180, angle_unit=True, grid=self.grid, priority=self.priority)
        self._internal_objects = [arc1, arc2]
        if self.length > 0:
            wg3 = Waveguide(
                xlength=self.width_r,
                ylength=self.ylength,
                zlength=self.length,
                x=self.x - self.outer_r + int(self.width_r / 2),
                y=self.y,
                z=self.z,
                width=self.width_r,
                name="%s_waveguide3" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                priority=self.priority
            )

            wg4 = Waveguide(
                xlength=self.width_r,
                ylength=self.ylength,
                zlength=self.length,
                x=self.x + self.outer_r - int(self.width_r / 2),
                y=self.y,
                z=self.z,
                width=self.width_r,
                name="%s_waveguide4" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                priority=self.priority
            )

            self._internal_objects += [wg3, wg4]

        wg_bottom = Waveguide(
            xlength=self.width,
            ylength=self.ylength,
            zlength=self.length_s,
            x=self.x - self.outer_r - self.gap - int(self.width / 2),
            y=self.y,
            z=self.z,
            width=self.width,
            name="%s_waveguide1" % self.name,
            refractive_index=self.refractive_index,
            grid=self.grid,
            priority=self.priority
        )

        wg_top = Waveguide(
            xlength=self.width,
            ylength=self.ylength,
            zlength=self.length_s,
            x=self.x + self.outer_r + self.gap + int(self.width / 2),
            y=self.y,
            z=self.z,
            width=self.width,
            name="%s_waveguide2" % self.name,
            refractive_index=self.refractive_index,
            grid=self.grid,
            priority=self.priority
        )

        # self.x = self.x - int(self.xlength / 2)
        # self.y = self.y - int(self.ylength / 2)
        # self.z = self.z - int(self.zlength / 2)

        self._internal_objects += [wg_top, wg_bottom]

    def _set_objects(self):
        self._internal_objects += []
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
        #     m = bd.zeros((self.outer_r * 2, self.zlength, self.outer_r * 2 + self.length))
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

