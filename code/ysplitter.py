from waveguide import Waveguide
import sbend
import numpy as np
import fdtd


class Trapezoid(Waveguide):
    """梯形（锥形）耦合部分代码，继承自waveguide
    xlength: 多模波导区域水平方向宽度 (在python fdtd包中, x方向为竖直方向，y为水平方向)
    ylength: 多模波导区域竖直方向宽度
    zlength: 多模波导区域z方向宽度，通常也是波导高度
    x,y,z: 多模波导位置坐标（通常是矩形区域最靠近原点的点）
    flag: 表示方向, flag = 1表示窄口在上（x轴负方向），flag = -1表示窄口在下（x轴正方向）
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
        flag=1,
        width=10,
        name="waveguide",
        refractive_index=1.7,
    ):

        Waveguide.__init__(self, xlength, ylength, zlength, x, y, z, flag, width, name, refractive_index)
        self.ylength = ylength
        self.xlength = xlength

    def set_grid(self):
        """输入波导规格，返回介电常数矩阵
        width:波导窄处宽度
        ylength:波导宽处宽度"""
        x = np.linspace(0, self.xlength, self.xlength)
        y = np.linspace(0, self.ylength, self.ylength)
        X, Y = np.meshgrid(x, y, indexing="ij")

        m = np.zeros((self.xlength, self.ylength, 1))

        if self.flag == 1:
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

        if self.flag == -1:
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

        result = {
            "name": self.name,
            "permittivity": permittivity,
            "size": (self.xlength, self.ylength, self.zlength),
            "position": (self.x, self.y, self.z),
            "flag": self.flag,
        }

        return result


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
        flag=1,
        width=10,
        name="waveguide",
        refractive_index=1.7,
        xlength_rectangle=30,
        xlength_trapezoid=10,
        ylength_trapezoid=30,
        xlength_sbend=30,
        ylength_sbend=30,
    ):
        Waveguide.__init__(self, xlength, ylength, zlength, x, y, z, flag, width, name, refractive_index)
        self.xlength_rectangle = xlength_rectangle
        self.xlength_trapezoid = xlength_trapezoid
        self.ylength_trapezoid = ylength_trapezoid
        self.xlength_sbend = xlength - xlength_rectangle - xlength_trapezoid
        self.ylength_sbend = int(ylength / 2 - ylength_trapezoid / 2 + width + 0.5)
        # self.xlength_sbend = xlength_sbend
        # self.ylength_sbend = ylength_sbend

    def set_grid(self):

        """返回四个部分的名称、介电常数矩阵、规格、位置，分别为直波导、梯形、s波导1、s波导2"""
        if self.flag == 1:
            waveguide = Waveguide(
                xlength=self.xlength_rectangle,
                ylength=self.width,
                zlength=self.zlength,
                x=self.x,
                y=self.y + int(self.ylength / 2 - self.width / 2 + 0.5),
                z=self.z,
                flag=self.flag,
                width=self.width,
                name="%s_waveguide" % self.name,
            )
            result_waveguide = waveguide.set_grid()
            trapezoid = Trapezoid(
                xlength=self.xlength_trapezoid,
                ylength=self.ylength_trapezoid,
                zlength=self.zlength,
                x=self.x + self.xlength_rectangle,
                y=self.y + int(self.ylength / 2 - self.ylength_trapezoid / 2 + 0.5),
                z=self.z,
                flag=self.flag,
                width=self.width,
                name="%s_trapezoid" % self.name,
            )
            result_trapezoid = trapezoid.set_grid()
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x + self.xlength_rectangle + self.xlength_trapezoid,
                y=self.y,
                z=self.z,
                flag=-self.flag,
                width=self.width,
                name="%s_sbend1" % self.name,
            )
            result_sbend1 = sbend1.set_grid()
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x + self.xlength_rectangle + self.xlength_trapezoid,
                y=self.y + self.ylength - self.ylength_sbend,
                z=self.z,
                flag=self.flag,
                width=self.width,
                name="%s_sbend2" % self.name,
            )
            result_sbend2 = sbend2.set_grid()
        else:
            waveguide = Waveguide(
                xlength=self.xlength_rectangle,
                ylength=self.width,
                zlength=self.zlength,
                x=self.x + self.xlength_sbend + self.xlength_trapezoid,
                y=self.y + int(self.ylength / 2 - self.width / 2 + 0.5),
                z=self.z,
                flag=self.flag,
                width=self.width,
                name="%s_waveguide" % self.name,
            )
            result_waveguide = waveguide.set_grid()
            trapezoid = Trapezoid(
                xlength=self.xlength_trapezoid,
                ylength=self.ylength_trapezoid,
                zlength=self.zlength,
                x=self.x + self.xlength_sbend,
                y=self.y + int(self.ylength / 2 - self.ylength_trapezoid / 2 + 0.5),
                z=self.z,
                flag=self.flag,
                width=self.width,
                name="%s_trapezoid" % self.name,
            )
            result_trapezoid = trapezoid.set_grid()
            sbend1 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x,
                y=self.y,
                z=self.z,
                flag=-self.flag,
                width=self.width,
                name="%s_sbend1" % self.name,
            )
            result_sbend1 = sbend1.set_grid()
            sbend2 = sbend.Sbend(
                xlength=self.xlength_sbend,
                ylength=self.ylength_sbend,
                zlength=self.zlength,
                x=self.x,
                y=self.y + self.ylength - self.ylength_sbend,
                z=self.z,
                flag=self.flag,
                width=self.width,
                name="%s_sbend2" % self.name,
            )
            result_sbend2 = sbend2.set_grid()

        return result_waveguide, result_trapezoid, result_sbend1, result_sbend2


if __name__ == "__main__":
    trapezoid = Trapezoid(xlength=10, ylength=8, zlength=1, x=10, y=50, z=1, flag=1, width=2, name="trapezoid")
    grid = trapezoid.set_grid()
    print(grid)

    ysplitter = Ysplitter(
        xlength=60,
        ylength=60,
        zlength=1,
        x=10,
        y=10,
        z=1,
        flag=-1,
        width=10,
        name="ysplitter",
        refractive_index=1.7,
        xlength_rectangle=20,
        xlength_trapezoid=10,
        ylength_trapezoid=20,
        xlength_sbend=30,
        ylength_sbend=30,
    )
    p1, p2, p3, p4 = ysplitter.set_grid()
    # print(p1['permittivity'][:,:,0])

    grid = fdtd.Grid(shape=(80, 80, 1), grid_spacing=155e-9)

    grid[
        p1["position"][0] : p1["position"][0] + p1["size"][0], p1["position"][1] : p1["position"][1] + p1["size"][1]
    ] = fdtd.Object(permittivity=p1["permittivity"], name=p1["name"])

    grid[
        p2["position"][0] : p2["position"][0] + p2["size"][0], p2["position"][1] : p2["position"][1] + p2["size"][1]
    ] = fdtd.Object(permittivity=p2["permittivity"], name=p2["name"])

    grid[
        p3["position"][0] : p3["position"][0] + p3["size"][0], p3["position"][1] : p3["position"][1] + p3["size"][1]
    ] = fdtd.Object(permittivity=p3["permittivity"], name=p3["name"])

    grid[
        p4["position"][0] : p4["position"][0] + p4["size"][0], p4["position"][1] : p4["position"][1] + p4["size"][1]
    ] = fdtd.Object(permittivity=p4["permittivity"], name=p4["name"])

    PML_width = 5

    grid[0:PML_width, :, :] = fdtd.PML(name="pml_xlow")
    grid[-PML_width:, :, :] = fdtd.PML(name="pml_xhigh")
    grid[:, 0:PML_width, :] = fdtd.PML(name="pml_ylow")
    grid[:, -PML_width:, :] = fdtd.PML(name="pml_yhigh")

    grid[60:60, 35:45] = fdtd.LineSource(period=1550e-9 / 299792458, name="source")

    # grid[55:55, 28:28] = fdtd.PointSource(
    # period=5.16e-15, name="sourced")

    grid.run(total_time=200)
    grid.visualize(z=0, show=True)
