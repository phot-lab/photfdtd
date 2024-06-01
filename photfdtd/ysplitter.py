from .waveguide import Waveguide
from . import sbend
import numpy as np


class Taper(Waveguide):
    """inverse taper
    梯形（锥形）耦合部分代码，继承自waveguide
    xlength/xlength_upper: 远处x宽度
    width/xlength_lower：近处x宽度
    ylength: 高度
    zlength: 长度
    x,y,z: 中心坐标
    refractive_index:折射率
    priority: the priority of the waveguide( high index indicates high priority)
    """

    def __init__(
            self,
            xlength_upper: int or float = None,
            xlength_lower: int or float = None,
            xlength: int or float = 40,
            width: int or float = 20,
            ylength: int or float = 40,
            zlength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            name: str = "taper",
            refractive_index: float = 3.47,
            grid=None,
            priority: int = 1
    ):
        if xlength_upper == None:
            xlength_upper = xlength
        if xlength_lower == None:
            xlength_lower = width

        # if xlength_high >= xlength_low:
        xlength = max(xlength_upper, xlength_lower)
        width = min(xlength_upper, xlength_lower)
        self.direction = bool(xlength_upper >= xlength_lower)
        # else:
        #     xlength = xlength_low
        #     width = xlength_high
        #     self.direction = -1
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, grid=grid, priority=priority)

    def _compute_permittivity(self):

        z = np.linspace(0, self.zlength, self.zlength)
        x = np.linspace(0, self.xlength, self.xlength)
        Z, X = np.meshgrid(z, x, indexing="ij")

        m = np.zeros((self.xlength, self.ylength, self.zlength))

        if self.direction:
            # 开口向z正方向
            for i in range(self.zlength):
                for j in range(self.xlength):
                    if (
                            Z[i, j] * (self.width / 2 - self.xlength / 2) / self.zlength
                            + self.xlength / 2
                            - self.width / 2
                            <= X[i, j]
                            <= Z[i, j] * (-self.width / 2 + self.xlength / 2) / self.zlength
                            + self.xlength / 2
                            + self.width / 2
                    ):
                        m[j, :, i] = True

        if not self.direction:
            # 开口向z负方向
            for i in range(self.zlength):
                for j in range(self.xlength):
                    if (
                            Z[self.zlength - i - 1, j] * (self.width / 2 - self.xlength / 2) / self.zlength
                            + self.xlength / 2
                            - self.width / 2
                            <= X[i, j]
                            <= Z[self.zlength - i - 1, j] * (-self.width / 2 + self.xlength / 2) / self.zlength
                            + self.xlength / 2
                            + self.width / 2
                    ):
                        m[j, :, i] = True

        permittivity = np.ones((self.xlength, self.ylength, self.zlength))
        permittivity += m * (self.refractive_index ** 2 - 1)
        permittivity += (1 - m) * (self.background_index ** 2 - 1)

        self.permittivity = permittivity


class Ysplitter(Waveguide):
    """
    Ysplitter or Ybranch, cascaded by a Taper and 2 Sbends
    Y分支波导，由一段直波导，一个梯形taper，两个S波导组成
    x, y, z：taper中心坐标
    xlength: 区域x方向全长,
    ylength: 区域y方向全长/厚度,
    zlength: 区域x方向全长/长度,
    direction=1：方向，1表示单端口在近，-1表示单端口在远
    width：直波导宽度
    name：名称
    refractive_index：折射率
    zlength_waveguide: 矩形区域z方向长度，
    xlength_taper：taper x方向长度,
    xlength_sbend：Sbend x方向长度,
    zlength_taper：taper z方向长度,
    zlength_sbend：Sbend z方向长度,
    width_sbend: sbend的波导宽度,
    priority: the priority of the waveguide( high index indicates high priority)
    """

    def __init__(
            self,
            xlength: int or float = None,
            ylength: int or float = None,
            zlength: int or float = None,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            direction: int = 1,
            width: int or float = 20,
            name: str = "ysplitter",
            refractive_index: float = 3.47,
            xlength_taper: int or float = 40,
            xlength_sbend: int or float = None,
            zlength_taper: int or float = 40,
            zlength_waveguide: int or float = 80,
            zlength_sbend: int or float = None,
            width_sbend: int or float = 20,
            grid=None,
            priority: int = 1
    ):
        xlength, ylength, zlength, width, zlength_waveguide, zlength_taper, xlength_taper, width_sbend, xlength_sbend, zlength_sbend = \
            grid._handle_unit(
                [xlength, ylength, zlength, width, zlength_waveguide, zlength_taper, xlength_taper, width_sbend,
                 xlength_sbend, zlength_sbend],
                grid_spacing=grid._grid.grid_spacing)
        self.direction = direction
        self.zlength_waveguide = zlength_waveguide
        self.zlength_taper = zlength_taper
        self.xlength_taper = xlength_taper

        if zlength_sbend is not None:
            self.zlength_sbend = zlength_sbend
            zlength = self.zlength_waveguide + self.zlength_taper + self.zlength_sbend
        else:
            self.zlength_sbend = zlength - zlength_waveguide - zlength_taper
        if xlength_sbend is not None:
            self.xlength_sbend = xlength_sbend
            xlength = self.xlength_sbend * 2 - width_sbend * 2 + xlength_taper
        else:
            self.xlength_sbend = int(xlength / 2 - xlength_taper / 2 + width_sbend + 0.5)
        self.width_sbend = width_sbend

        super().__init__(xlength, ylength, zlength, x, y, z,
                         width, name, refractive_index, grid=grid, reset_xyz=False, priority=priority)

    def _set_objects(self):

        """"""
        if self.direction == 1:
            waveguide = Waveguide(
                xlength=self.width,
                ylength=self.ylength,
                zlength=self.zlength_waveguide,
                x=self.x,
                y=self.y,
                z=self.z - int(self.zlength_taper / 2 + self.zlength_waveguide / 2),
                width=self.width,
                name="%s_waveguide" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                priority=self.priority
            )
            taper = Taper(xlength=self.xlength_taper, width=self.width, ylength=self.ylength,
                          zlength=self.zlength_taper + 2, x=self.x, y=self.y, z=self.z, name="%s_taper" % self.name,
                          refractive_index=self.refractive_index, grid=self.grid, priority=self.priority)
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength,
                zlength=self.zlength_sbend,
                x=self.x + int(self.xlength_taper / 2 + self.xlength_sbend / 2) - self.width_sbend,
                y=self.y,
                z=self.z + int(self.zlength_taper / 2 + self.zlength_sbend / 2),
                direction=self.direction,
                width=self.width_sbend,
                name="%s_sbend1" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                center_postion=True,
                priority=self.priority
            )
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength,
                zlength=self.zlength_sbend,
                x=self.x - int(self.xlength_taper / 2 + self.xlength_sbend / 2) + self.width_sbend,
                y=self.y,
                z=self.z + int(self.zlength_taper / 2 + self.zlength_sbend / 2),
                direction=-self.direction,
                width=self.width_sbend,
                name="%s_sbend2" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                center_postion=True,
                priority=self.priority
            )
        else:
            waveguide = Waveguide(
                xlength=self.width,
                ylength=self.ylength,
                zlength=self.zlength_waveguide,
                x=self.x,
                y=self.y,
                z=self.z + int(self.zlength_waveguide / 2 + self.zlength_taper / 2),
                width=self.width,
                name="%s_waveguide" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                priority=self.priority
            )
            taper = Taper(xlength=self.xlength_taper, width=self.width, ylength=self.ylength,
                          zlength=self.zlength_taper, x=self.x, y=self.y, z=self.z, name="%s_trapezoid" % self.name,
                          refractive_index=self.refractive_index, grid=self.grid, priority=self.priority)
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength,
                zlength=self.zlength_sbend,
                x=self.x + int(self.xlength_taper / 2 + self.xlength_sbend / 2 - self.width_sbend),
                y=self.y,
                z=self.z - int(self.zlength_taper / 2) - int(self.zlength_sbend / 2),
                direction=self.direction,
                width=self.width,
                name="%s_sbend1" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                center_postion=True,
                priority=self.priority
            )
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength,
                zlength=self.zlength_sbend,
                x=self.x - int(self.xlength_taper / 2 + self.xlength_sbend / 2 - self.width_sbend),
                y=self.y,
                z=self.z - int(self.zlength_taper / 2) - int(self.zlength_sbend / 2),
                direction=-self.direction,
                width=self.width,
                name="%s_sbend2" % self.name,
                refractive_index=self.refractive_index,
                grid=self.grid,
                center_postion=True,
                priority=self.priority
            )

        self._internal_objects = [waveguide, taper, sbend1, sbend2]
