from .waveguide import Waveguide
import numpy as np
import photfdtd.fdtd as fdtd


class SbendShape(Waveguide):
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
        xlength: int = 60,
        ylength: int = 10,
        zlength: int = 10,
        x: int = 50,
        y: int = 50,
        z: int = 50,
        width: int = 10,
        name: str = "waveguide",
        refractive_index: float = 1.7,
        direction: int = -1,
    ):
        self.direction = direction
        super().__init__(
            xlength, ylength, zlength, x, y, z, width, name, refractive_index
        )

    # def _compute_permittivity(self):
    #     """
    #     输入波导规格，返回字典，包含名字、介电常数矩阵（规格为[ylength,xlength,zlength]）、区域规格、位置坐标、direction(=1表示形状左上至右下，=-1表示形状从左下到右上)
    #     """
    #     x = np.linspace(0, self.xlength, self.xlength)
    #     y = np.linspace(0, self.ylength, self.ylength)
    #     X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
    #     m = np.zeros((self.xlength, self.ylength, self.zlength))
    #
    #     if self.direction == 1:
    #         # direction=1, 波导方向从左上到右下
    #
    #         m1 = (
    #             Y
    #             <= 0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
    #             + self.width / 2
    #             + self.ylength / 2
    #         )
    #
    #         m2 = (
    #             Y
    #             >= 0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
    #             - self.width / 2
    #             + self.ylength / 2
    #         )
    #     elif self.direction == -1:
    #         # direction=-1, 波导方向从左下到右上
    #         m1 = (
    #             Y
    #             <= -0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
    #             + self.width / 2
    #             + self.ylength / 2
    #         )
    #         m2 = (
    #             Y
    #             >= -0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
    #             - self.width / 2
    #             + self.ylength / 2
    #         )
    #     else:
    #         raise RuntimeError("Unknown direction")
    #
    #     for i in range(self.xlength):
    #         for j in range(self.ylength):
    #             if m1[i, j] == m2[i, j]:
    #                 m[i, j, :] = True
    #
    #     permittivity = np.ones((self.xlength, self.ylength, self.zlength))
    #     permittivity += m[:, :] * (self.refractive_index**2 - 1)
    #
    #     self.permittivity = permittivity

    def _set_objects(self):
        self._internal_objects = []
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
                <= 0.5
                * (self.ylength - self.width)
                * np.sin((X / self.xlength - 0.5) * np.pi)
                + self.width / 2
                + self.ylength / 2
            )

            m2 = (
                Y
                >= 0.5
                * (self.ylength - self.width)
                * np.sin((X / self.xlength - 0.5) * np.pi)
                - self.width / 2
                + self.ylength / 2
            )
        elif self.direction == -1:
            # direction=-1, 波导方向从左下到右上
            m1 = (
                Y
                <= -0.5
                * (self.ylength - self.width)
                * np.sin((X / self.xlength - 0.5) * np.pi)
                + self.width / 2
                + self.ylength / 2
            )
            m2 = (
                Y
                >= -0.5
                * (self.ylength - self.width)
                * np.sin((X / self.xlength - 0.5) * np.pi)
                - self.width / 2
                + self.ylength / 2
            )
        else:
            raise RuntimeError("Unknown direction")

        for i in range(self.xlength):
            border_t = -1
            border_d = self.ylength - 1
            last_state = False
            in_shape = False
            for j in range(self.ylength):
                last_state = in_shape
                if m1[i, j] == m2[i, j]:
                    in_shape = True
                    if last_state == False:
                        border_t = j
                else:
                    in_shape = False
                    if last_state == True:
                        border_d = j - 1
            if border_t != -1:
                # print(border_d)
                # print(border_t)
                waveguide = Waveguide(
                    xlength=1,
                    ylength=border_d - border_t + 1,
                    zlength=1,
                    x=self.x + i,
                    y=self.y + border_t,
                    z=0,
                    name="ArcShape" + str(i),
                    refractive_index=self.refractive_index,
                )
                self._internal_objects.append(waveguide)
