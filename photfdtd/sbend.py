from .waveguide import Waveguide
import numpy as np
import fdtd


class Sbend(Waveguide):

    """s波导代码，继承自waveguide
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    direction: =1表示形状左上至右下，=-1表示形状从左下到右上
    width：波导宽度
    refractive_index:折射率"""

    def __init__(
        self,
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        width=10,
        name="waveguide",
        refractive_index=1.7,
        direction=-1,
    ):
        self.direction = direction
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index)

    def _compute_permittivity(self):
        """
        输入波导规格，返回字典，包含名字、介电常数矩阵（规格为[ylength,xlength,zlength]）、区域规格、位置坐标、direction(=1表示形状左上至右下，=-1表示形状从左下到右上)
        """
        x = np.linspace(0, self.xlength, self.xlength)
        y = np.linspace(0, self.ylength, self.ylength)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
        m = np.zeros((self.xlength, self.ylength, self.zlength))

        if self.direction == 1:
            # direction=1, 波导方向从左上到右下

            m1 = (
                Y
                <= 0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                + self.width / 2
                + self.ylength / 2
            )

            m2 = (
                Y
                >= 0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                - self.width / 2
                + self.ylength / 2
            )

        if self.direction == -1:
            # direction=-1, 波导方向从左下到右上
            m1 = (
                Y
                <= -0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                + self.width / 2
                + self.ylength / 2
            )
            m2 = (
                Y
                >= -0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                - self.width / 2
                + self.ylength / 2
            )

        for i in range(self.xlength):
            for j in range(self.ylength):
                if m1[i, j] == m2[i, j]:
                    m[i, j, :] = True

        permittivity = np.ones((self.xlength, self.ylength, self.zlength))
        permittivity += m[:, :] * (self.refractive_index**2 - 1)

        self.permittivity = permittivity

    def set_source(self):
        if self.direction == 1:
            self._grid[11:11, self.y : self.y + 10] = fdtd.LineSource(period=1550e-9 / 299792458, name="source")
        else:
            self._grid[11 + self.xlength : 11 + self.xlength, self.y : self.y + 10] = fdtd.LineSource(
                period=1550e-9 / 299792458, name="source"
            )
