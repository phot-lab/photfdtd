from .waveguide import Waveguide
import numpy as np


class Sbend(Waveguide):
    """
    s波导代码，继承自waveguide
    xlength: x跨度
    ylength: 厚度
    zlength: 长度
    x,y,z: 中心坐标
    direction:
    width：波导宽度
    refractive_index: 折射率
    grid: grid
    direction: 1 or -1, 波导方向从左下到右上或~
    """
    # TODO: 像Rsoft里那样设置sbend。The settings of Sbend should be like that in Rsoft.
    def __init__(
            self,
            xlength: int or float = None,
            ylength: int or float = None,
            zlength: int or float = None,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width: int or float = 20,
            name: str = "sbend",
            refractive_index: float = 3.47,
            direction: int = 1,
            grid=None
    ) -> None:
        self.direction = direction
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, grid=grid)

    def _compute_permittivity(self):
        """
        """
        z = np.linspace(0, self.zlength, self.zlength)
        x = np.linspace(0, self.xlength, self.xlength)
        Z, X = np.meshgrid(z, x, indexing="ij")  # indexing = 'ij'很重要
        m = np.zeros((self.xlength, self.ylength, self.zlength))

        if self.direction == 1:
            # direction=1, 波导方向从左下到右上
            m1 = (
                    X
                    <= 0.5 * (self.xlength - self.width) * np.sin((Z / self.zlength - 0.5) * np.pi)
                    + int(self.width / 2 + 0.5)
                    + self.xlength / 2
            )
            # 上下翻转
            m2 = np.flipud(m1)
            # 左右翻转
            m2 = np.fliplr(m2)

            # m2 = (
            #         X
            #         <= 0.5 * (self.xlength - self.width) * np.sin((Z / self.zlength - 0.5) * np.pi)
            #         - int(self.width / 2 + 0.5)
            #         + self.xlength / 2
            # )

            # m2 = (
            #     X
            #     >= 0.5 * (self.xlength - self.width) * np.sin((Z / self.zlength - 0.5) * np.pi)
            #     - self.width / 2
            #     + self.xlength / 2
            # )
        elif self.direction == -1:
            # direction=-1, 波导方向从左上到右下
            m1 = (
                    X
                    <= -0.5 * (self.xlength - self.width) * np.sin((Z / self.zlength - 0.5) * np.pi)
                    + int(self.width / 2 + 0.5)
                    + self.xlength / 2
            )
            # 上下翻转
            m2 = np.flipud(m1)
            # 左右翻转
            m2 = np.fliplr(m2)
            # m2 = (
            #     X
            #     >= -0.5 * (self.xlength - self.width) * np.sin((Z / self.zlength - 0.5) * np.pi)
            #     - self.width / 2
            #     + self.xlength / 2
            # )
        else:
            raise RuntimeError("Unknown direction")

        for i in range(self.zlength):
            for j in range(self.xlength):
                if m1[i, j] == m2[i, j]:
                    m[j, :, i] = True

        permittivity = np.ones((self.xlength, self.ylength, self.zlength))
        permittivity += m[:, :] * (self.refractive_index ** 2 - 1)
        permittivity += (1 - m[:, :]) * (self.background_index ** 2 - 1)

        self.permittivity = permittivity
