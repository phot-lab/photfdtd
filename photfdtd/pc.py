import numpy as np
from .fiber import Fiber


class Hexagonal_PC():
    """六边形方格光子晶体(Hexagonal Photonic Crystal)
    n_side: number of crystals on each side of the hexagon
    H_number: number of rings missing that form a cavity
    zlength: height of each crystal
    a: lattice constant 晶格常数，在本结构中是光子晶体中心的间距
    radius: radius of the crystals
    x,y,z: 中心坐标
    refractive_index: 折射率
    name: 名称
    background_index: 环境折射率
    """

    # TODO：现在只有x-y平面

    def __init__(
            self,
            n_side: int = None,
            H_number: int = None,
            zlength: int = None,
            a: int = None,
            radius: int = None,
            x: int = 100,
            y: int = 100,
            z: int = 1,
            refractive_index: float = 3.47,
            name: str = "arc",
            background_index: float = 1.0,
    ) -> None:
        # TODO: FIXME: NOTE: python中赋值后面加逗号代表创建元组
        self.n_side = n_side
        self.H_number = H_number
        self.a = a
        self.zlength = zlength
        self.x, self.x_center = x, x
        self.y, self.y_center = y, y
        self.z, self.z_center = z, z
        self.radius = radius
        self.refractive_index = refractive_index
        self.name = name
        self.background_index = background_index

        self._set_objects()

    def _set_objects(self):
        """"""
        n_y = self.n_side
        n_x = 2 * n_y
        self._internal_objects = []
        # 计数器，用于给光子晶体们命名
        flag = 0
        # draw center row
        # for j in range(-n_y, n_y, 1):
        #     if j >= self.H_number | j < -self.H_number:
        #         circle = Fiber(radius=[self.radius], length=self.zlength,x=self.x + j * self.a,y=self.y,z=self.z,
        #                        refractive_index=[self.refractive_index], name="%s_circle%d" % (self.name, flag),
        #                        axis="z", background_index=self.background_index)
        #         flag+=1
        #         self._internal_objects.append(circle)
        #         # addcircle;
        #         # set("x", (j) * a );
        #         # set("y", 0);

        # draw upper and lower rows
        for i in range(n_y):
            n_x -= 1
            # +1/2 确保形状正确且整个结构中心不偏移
            for j in np.arange(-n_x / 2 + 1 / 2, n_x / 2 + 1 / 2, 1):
                if i < self.H_number:
                    if j >= (self.H_number - i / 2) or j <= -(self.H_number - i / 2):
                        circle = Fiber(radius=[self.radius], length=self.zlength, x=self.x + j * self.a,
                                       y=self.y + i * self.a * np.sqrt(3) / 2, z=self.z,
                                       refractive_index=[self.refractive_index], name="%s_circle_%d" % (self.name, flag),
                                       axis="z", background_index=self.background_index)
                        flag+=1
                        self._internal_objects.append(circle)
                        circle = Fiber(radius=[self.radius], length=self.zlength, x=self.x + j * self.a,
                                       y=self.y - i * self.a * np.sqrt(3) / 2, z=self.z,
                                       refractive_index=[self.refractive_index], name="%s_circle_%d" % (self.name, flag),
                                       axis="z", background_index=self.background_index)
                        flag += 1
                        self._internal_objects.append(circle)
                else:
                    circle = Fiber(radius=[self.radius], length=self.zlength, x=self.x + j * self.a,
                                   y=self.y + i * self.a * np.sqrt(3) / 2, z=self.z,
                                   refractive_index=[self.refractive_index], name="%s_circle_%d" % (self.name, flag),
                                   axis="z", background_index=self.background_index)
                    flag += 1
                    self._internal_objects.append(circle)
                    circle = Fiber(radius=[self.radius], length=self.zlength, x=self.x + j * self.a,
                                   y=self.y - i * self.a * np.sqrt(3) / 2, z=self.z,
                                   refractive_index=[self.refractive_index], name="%s_circle_%d" % (self.name, flag),
                                   axis="z", background_index=self.background_index)
                    flag += 1
                    self._internal_objects.append(circle)


