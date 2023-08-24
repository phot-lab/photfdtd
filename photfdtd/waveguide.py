import numpy as np
import fdtd
import matplotlib.pyplot as plt


class Waveguide:
    """
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    width：波导宽度(在矩形波导中，波导宽度没有意义)
    refractive_index:折射率
    name:名称
    ！！！x，y仍然对应FDTD包中的x，y轴！！！
    """

    def __init__(
        self,
        xlength: int = 60,
        ylength: int = 10,
        zlength: int = 10,
        x: int = 50,
        y: int = 50,
        z: int = 50,
        width: int = 10,
        name: str = "waveguide",
        refractive_index: float = 1.7,
    ):
        self.xlength = xlength
        self.ylength = ylength
        self.zlength = zlength
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.name = name
        self.refractive_index = refractive_index

        self._compute_permittivity()
        self._set_objects()

    def _compute_permittivity(self):
        """矩形波导"""
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
        permittivity += self.refractive_index**2

        self.permittivity = permittivity

    def _set_objects(self):
        self._internal_objects = [self]
