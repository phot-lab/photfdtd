from .waveguide import Waveguide
from . import sbend
import numpy as np
import fdtd


class Trapezoid(Waveguide):
    """梯形（锥形）耦合部分代码，继承自waveguide
    xlength: 多模波导区域水平方向宽度 (在python fdtd包中, x方向为竖直方向，y为水平方向)
    ylength: 多模波导区域竖直方向宽度
    zlength: 多模波导区域z方向宽度，通常也是波导高度
    x,y,z: 多模波导位置坐标（通常是矩形区域最靠近原点的点）
    direction: 表示方向, direction = 1表示窄口在上（x轴负方向），direction = -1表示窄口在下（x轴正方向）
    width：窄处宽度
    refractive_index:折射率"""

    def __init__(
        self,
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        direction=1,
        width=10,
        name="waveguide",
        refractive_index=1.7,
    ):

        self.direction = direction
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index)

    def _compute_permittivity(self):
        """输入波导规格，返回介电常数矩阵
        width:波导窄处宽度
        ylength:波导宽处宽度"""
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
        permittivity += m[:, :] * (self.refractive_index**2 - 1)

        self.permittivity = permittivity


class Ysplitter(Waveguide):

    """Y分支波导，由一段直波导，一个梯形，两个S波导组成"""

    def __init__(
        self,
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        direction=-1,
        width=10,
        name="ysplitter",
        refractive_index=1.7,
        xlength_rectangle=30,
        xlength_trapezoid=10,
        ylength_trapezoid=30,
    ):
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index)
        self.direction = direction
        self.xlength_rectangle = xlength_rectangle
        self.xlength_trapezoid = xlength_trapezoid
        self.ylength_trapezoid = ylength_trapezoid
        self.xlength_sbend = xlength - xlength_rectangle - xlength_trapezoid
        self.ylength_sbend = int(ylength / 2 - ylength_trapezoid / 2 + width + 0.5)

    def set_grid(
        self, grid_ylength=80, grid_xlength=80, grid_zlength=1, grid_spacing=155e-9, total_time=200, pml_width=10
    ):

        """返回四个部分的名称、介电常数矩阵、规格、位置，分别为直波导、梯形、s波导1、s波导2"""
        if self.direction == 1:
            waveguide = Waveguide(
                xlength=self.xlength_rectangle,
                ylength=self.width,
                zlength=self.zlength,
                x=self.x,
                y=self.y + int(self.ylength / 2 - self.width / 2 + 0.5),
                z=self.z,
                width=self.width,
                name="%s_waveguide" % self.name,
            )
            # waveguide.set_grid()
            trapezoid = Trapezoid(
                xlength=self.xlength_trapezoid,
                ylength=self.ylength_trapezoid,
                zlength=self.zlength,
                x=self.x + self.xlength_rectangle,
                y=self.y + int(self.ylength / 2 - self.ylength_trapezoid / 2 + 0.5),
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_trapezoid" % self.name,
            )
            # trapezoid.set_grid()
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x + self.xlength_rectangle + self.xlength_trapezoid,
                y=self.y,
                z=self.z,
                direction=-self.direction,
                width=self.width,
                name="%s_sbend1" % self.name,
            )
            # sbend1.set_grid()
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x + self.xlength_rectangle + self.xlength_trapezoid,
                y=self.y + self.ylength - self.ylength_sbend,
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_sbend2" % self.name,
            )
            # sbend2.set_grid()
        else:
            waveguide = Waveguide(
                xlength=self.xlength_rectangle,
                ylength=self.width,
                zlength=self.zlength,
                x=self.x + self.xlength_sbend + self.xlength_trapezoid,
                y=self.y + int(self.ylength / 2 - self.width / 2 + 0.5),
                z=self.z,
                width=self.width,
                name="%s_waveguide" % self.name,
            )
            # waveguide.set_grid()
            trapezoid = Trapezoid(
                xlength=self.xlength_trapezoid,
                ylength=self.ylength_trapezoid,
                zlength=self.zlength,
                x=self.x + self.xlength_sbend,
                y=self.y + int(self.ylength / 2 - self.ylength_trapezoid / 2 + 0.5),
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_trapezoid" % self.name,
            )
            # trapezoid.set_grid()
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x,
                y=self.y,
                z=self.z,
                direction=-self.direction,
                width=self.width,
                name="%s_sbend1" % self.name,
            )
            # sbend1.set_grid()
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x,
                y=self.y + self.ylength - self.ylength_sbend,
                z=self.z,
                direction=self.direction,
                width=self.width,
                name="%s_sbend2" % self.name,
            )
            # sbend2.set_grid()

        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength), grid_spacing=grid_spacing)

        grid[
            waveguide.x : waveguide.x + waveguide.xlength, waveguide.y : waveguide.y + waveguide.ylength
        ] = fdtd.Object(permittivity=waveguide.permittivity, name=waveguide.name)

        grid[
            trapezoid.x : trapezoid.x + trapezoid.xlength, trapezoid.y : trapezoid.y + trapezoid.ylength
        ] = fdtd.Object(permittivity=trapezoid.permittivity, name=trapezoid.name)

        grid[sbend1.x : sbend1.x + sbend1.xlength, sbend1.y : sbend1.y + sbend1.ylength] = fdtd.Object(
            permittivity=sbend1.permittivity, name=sbend1.name
        )

        grid[sbend2.x : sbend2.x + sbend2.xlength, sbend2.y : sbend2.y + sbend2.ylength] = fdtd.Object(
            permittivity=sbend2.permittivity, name=sbend2.name
        )

        grid[0:pml_width, :, :] = fdtd.PML(name="pml_xlow")
        grid[-pml_width:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
        grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")

        self._total_time = total_time
        self._grid = grid

    def set_source(self):
        self._grid[60:60, 35:45] = fdtd.LineSource(period=1550e-9 / 299792458, name="source")
