import numpy as np
from .waveguide import Waveguide


class Circle(Waveguide):
    # TODO: 由于在设置的波导中，非波导部分折射率都为1，因此目前设置空间折射率来改变包层折射率并无意义
    """圆波导
    radius: 半径
    length: 长度
    x,y,z: 位置坐标（中心）
    refractive_index:折射率
    name: 名称
    axis: 'x', 'y', 'z' 波导沿哪个轴
    """

    def __init__(
        self,
        radius: int,
        length: int,
        x: int,
        y: int,
        z: int,
        refractive_index: float,
        name: str,
        axis: str,
    ) -> None:
        self.radius = radius
        self.length = length
        self.axis = axis
        if self.axis == "x":
            # 在调用fdtd包时，仍然需要把x,y,z转换为最靠近原点的端点
            super().__init__(
                x=x - self.length / 2,
                y=y - self.radius,
                z=z - self.radius,
                name=name,
                refractive_index=refractive_index,
            )

        elif self.axis == "y":
            # 在调用fdtd包时，仍然需要把x,y,z转换为最靠近原点的端点
            super().__init__(
                x=x - self.radius,
                y=y - self.length / 2,
                z=z - self.radius,
                name=name,
                refractive_index=refractive_index,
            )
        elif self.axis == "z":
            # 在调用fdtd包时，仍然需要把x,y,z转换为最靠近原点的端点
            super().__init__(
                x=x - self.radius,
                y=y - self.radius,
                z=z - self.length / 2,
                name=name,
                refractive_index=refractive_index,
            )

    def _compute_permittivity(self):
        # 这里+2的原因：稍微扩大一点矩阵的大小，可以保证水平和竖直方向最边上的点不被丢出
        # TODO: 给其他带圆弧的波导相同的操作？
        x = y = np.linspace(1, 2 * self.radius + 2, 2 * self.radius + 2)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
        m = (X - len(x) / 2) ** 2 + (Y - len(y) / 2) ** 2 <= self.radius**2

        if self.axis.lower() == "x":
            # 波导沿x轴
            self.xlength = self.length
            self.ylength = 2 * self.radius + 2
            self.zlength = 2 * self.radius + 2
            self.permittivity = np.ones(
                (self.length, 2 * self.radius + 2, 2 * self.radius + 2)
            )
            for i in range(self.length):
                self.permittivity[i] += m[:, :] * (self.refractive_index**2 - 1)

        elif self.axis.lower() == "y":
            # 波导沿y轴
            self.xlength = 2 * self.radius + 2
            self.ylength = self.length
            self.zlength = 2 * self.radius + 2
            self.permittivity = np.ones(
                (2 * self.radius + 2, self.length, 2 * self.radius + 2)
            )
            for i in range(self.length):
                self.permittivity[:, i] += m[:, :] * (self.refractive_index**2 - 1)

        elif self.axis.lower() == "z":
            # 波导沿z轴
            self.xlength = 2 * self.radius + 2
            self.ylength = 2 * self.radius + 2
            self.zlength = self.length
            self.permittivity = np.ones(
                (2 * self.radius + 2, 2 * self.radius + 2, self.length)
            )
            for i in range(self.length):
                self.permittivity[:, :, i] += m[:, :] * (self.refractive_index**2 - 1)
