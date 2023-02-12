from .waveguide import Waveguide
import numpy as np
import fdtd


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
        outer_radius=60,
        zlength=10,
        x=50,
        y=50,
        z=50,
        width=5,
        length=0,
        gap=0,
        name="ring",
        refractive_index=3.47,
        direction=1,
    ):

        self.outer_r = outer_radius
        self.length = length
        self.gap = gap
        self.direction = direction
        super().__init__(zlength, zlength, zlength, x, y, z, width, name, refractive_index)

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

        self.permittivity = permittivity

    def set_grid(
        self, grid_xlength=120, grid_ylength=130, grid_zlength=1, grid_spacing=155e-9, total_time=1000, pml_width=5
    ):

        wg_bottom = Waveguide(
            xlength=self.outer_r * 2 + self.length,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            width=self.width,
            name="waveguide_bottom_%s" % self.name,
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
            name="waveguide_top_%s" % self.name,
            refractive_index=self.refractive_index,
        )

        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength), grid_spacing=grid_spacing)

        x = self.x
        xlength = self.outer_r * 2 + self.length
        y = self.y + self.width + self.gap
        ylength = self.outer_r * 2

        grid[
            x : x + xlength,
            y : y + ylength,
        ] = fdtd.Object(permittivity=self.permittivity, name=self.name)

        grid[
            wg_top.x : wg_top.x + wg_top.xlength,
            wg_top.y : wg_top.y + wg_top.ylength,
        ] = fdtd.Object(permittivity=wg_top.permittivity, name=wg_top.name)

        grid[
            wg_bottom.x : wg_bottom.x + wg_bottom.xlength,
            wg_bottom.y : wg_bottom.y + wg_bottom.ylength,
        ] = fdtd.Object(permittivity=wg_bottom.permittivity, name=wg_bottom.name)

        grid[0:pml_width, :, :] = fdtd.PML(name="pml_xlow")
        grid[-pml_width:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
        grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")

        grid[8:8, wg_bottom.y - 1 : wg_bottom.y + 6] = fdtd.LineSource(period=1550e-9 / 299792458, name="source")

        self._total_time = total_time
        self._grid = grid
