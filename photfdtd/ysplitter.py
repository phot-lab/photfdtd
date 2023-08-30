from .waveguide import Waveguide
from . import sbend
import numpy as np


class Taper(Waveguide):
    """梯形（锥形）耦合部分代码，继承自waveguide
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength:
    x,y,z: 中心坐标
    direction: 表示方向, direction = 1表示单端口在x轴负方向，direction = -1表示单端口在x轴正方向
    width：直波导宽度
    refractive_index:折射率
    background_index: """

    def __init__(
            self,
            xlength: int = 40,
            ylength: int = 40,
            zlength: int = 20,
            x: int = 50,
            y: int = 50,
            z: int = 50,
            direction: int = 1,
            width: int = 20,
            name: str = "taper",
            refractive_index: float = 3.47,
            background_index: float = 1
    ):

        self.direction = direction
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, background_index)

    def _compute_permittivity(self):

        x = np.linspace(0, self.xlength, self.xlength)
        y = np.linspace(0, self.ylength, self.ylength)
        X, Y = np.meshgrid(x, y, indexing="ij")

        m = np.zeros((self.xlength, self.ylength, 1))

        if self.direction == 1:
            # 开口向下（x正方向）
            for i in range(self.xlength):
                for j in range(self.ylength):
                    if (
                            X[i, j] * (self.width / 2 - self.ylength / 2) / self.xlength
                            + self.ylength / 2
                            - self.width / 2
                            <= Y[i, j]
                            <= X[i, j] * (-self.width / 2 + self.ylength / 2) / self.xlength
                            + self.ylength / 2
                            + self.width / 2
                    ):
                        m[i, j] = True

        if self.direction == -1:
            # 开口向上（x负方向）
            for i in range(self.xlength):
                for j in range(self.ylength):
                    if (
                            X[self.xlength - i - 1, j] * (self.width / 2 - self.ylength / 2) / self.xlength
                            + self.ylength / 2
                            - self.width / 2
                            <= Y[i, j]
                            <= X[self.xlength - i - 1, j] * (-self.width / 2 + self.ylength / 2) / self.xlength
                            + self.ylength / 2
                            + self.width / 2
                    ):
                        m[i, j] = True

        permittivity = np.ones((self.xlength, self.ylength, self.zlength))
        permittivity += m[:, :] * (self.refractive_index ** 2 - 1)
        permittivity += (1 - m[:, :]) * (self.background_index ** 2 - 1)

        self.permittivity = permittivity


class Ysplitter(Waveguide):
    """
    Y分支波导，由一段直波导，一个梯形taper，两个S波导组成
    x, y, z：taper中心坐标
    xlength: 波导区域x方向全长,
    ylength: 波导区域y方向全长,
    zlength: 波导厚度,
    direction=1：方向，1表示单端口在x轴负方向，-1表示单端口在x轴正方向
    width：直波导宽度
    name：名称
    refractive_index：折射率
    xlength_waveguide: 直（矩形）波导x方向长度，
    xlength_taper：taper x方向长度,
    ylength_taper：taper y方向长度,
    width_sbend: sbend的波导宽度,
    background_index: 环境折射率
    """

    def __init__(
            self,
            xlength: int = 200,
            ylength: int = 160,
            zlength: int = 20,
            x: int = 100,
            y: int = 100,
            z: int = 13,
            direction: int = 1,
            width: int = 20,
            name: str = "ysplitter",
            refractive_index: float = 3.47,
            xlength_waveguide: int = 80,
            xlength_taper: int = 40,
            ylength_taper: int = 40,
            width_sbend: int = 20,
            background_index: float = 1
    ):
        self.direction = direction
        self.xlength_waveguide = xlength_waveguide
        self.xlength_taper = xlength_taper
        self.ylength_taper = ylength_taper
        self.xlength_sbend = xlength - xlength_waveguide - xlength_taper
        self.ylength_sbend = int(ylength / 2 - ylength_taper / 2 + width_sbend + 0.5)
        self.width_sbend = width_sbend

        x = x + int(xlength / 2)
        y = y + int(ylength / 2)
        z = z + int(zlength / 2)

        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, background_index)

    def _set_objects(self):

        """"""
        if self.direction == 1:
            waveguide = Waveguide(
                xlength=self.xlength_waveguide,
                ylength=self.width,
                zlength=self.zlength,
                x=self.x - int(self.xlength_taper / 2 + self.xlength_waveguide / 2),
                y=self.y,
                z=self.z,
                width=self.width,
                name="%s_waveguide" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            taper = Taper(
                xlength=self.xlength_taper,
                ylength=self.ylength_taper,
                zlength=self.zlength,
                x=self.x,
                y=self.y,
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_trapezoid" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x + int(self.xlength_taper / 2 + self.xlength_sbend / 2),
                y=self.y + int(self.ylength_taper / 2 + self.ylength_sbend / 2) - self.width_sbend,
                z=self.z,
                direction=self.direction,
                width=self.width_sbend,
                name="%s_sbend1" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x + int(self.xlength_taper / 2 + self.xlength_sbend / 2),
                y=self.y - int(self.ylength_taper / 2 + self.ylength_sbend / 2) + self.width_sbend,
                z=self.z,
                direction=-self.direction,
                width=self.width,
                name="%s_sbend2" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
        else:
            waveguide = Waveguide(
                xlength=self.xlength_waveguide,
                ylength=self.width,
                zlength=self.zlength,
                x=self.x + int(self.xlength_waveguide / 2 + self.xlength_taper / 2),
                y=self.y,
                z=self.z,
                width=self.width,
                name="%s_waveguide" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            taper = Taper(
                xlength=self.xlength_taper,
                ylength=self.ylength_taper,
                zlength=self.zlength,
                x=self.x,
                y=self.y,
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_trapezoid" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x - int(self.xlength_taper / 2) - int(self.xlength_sbend / 2),
                y=self.y + int(self.ylength_taper / 2 + self.ylength_sbend / 2 - self.width_sbend),
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_sbend1" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x - int(self.xlength_taper / 2) - int(self.xlength_sbend / 2),
                y=self.y - int(self.ylength_taper / 2 + self.ylength_sbend / 2 - self.width_sbend),
                z=self.z,
                direction=-self.direction,
                width=self.width,
                name="%s_sbend2" % self.name,
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )

        self._internal_objects = [waveguide, taper, sbend1, sbend2]
