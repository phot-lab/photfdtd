import numpy as np
from .arc import Arc


class FWG():
    """扇形波导光栅(fan-shaped waveguide grating)
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 圆心坐标
    width: 波导宽度
    gap: 波导间距
    number: 波导数量
    refractive_index:折射率
    name: 名称
    direction: 等于1，2，3，4，分别表示四个方向
    angle_phi: 与x轴正方向夹角, 单位: 角度
    angle_psi: 张角(单位: 角度，必须小于90）
    background_index: 环境折射率
    """

    # TODO：现在只有x-y平面

    def __init__(
            self,
            outer_radius: int = 60,
            zlength: int = 20,
            x: int = 100,
            y: int = 100,
            z: int = 1,
            width: int = 20,
            refractive_index: float = 3.47,
            name: str = "arc",
            angle_phi: float = 0,
            angle_psi: float = 0,
            background_index: float = 1.0,
            gap: int = 1,
            number: int = None
    ) -> None:
        # TODO: FIXME: NOTE: python中赋值后面加逗号代表创建元组
        self.gap = gap
        self.number = number
        self.outer_radius = outer_radius
        self.zlength = zlength
        self.x, self.x_center = x, x
        self.y, self.y_center = y, y
        self.z, self.z_center = z, z
        self.width = width
        self.refractive_index = refractive_index
        self.name = name
        self.phi = angle_phi
        self.psi = angle_psi
        self.background_index = background_index

        self._set_objects()

    def _set_objects(self):
        self._internal_objects = []
        for i in range(self.number):
            arc = Arc(outer_radius=self.outer_radius - (self.gap + self.width) * i, zlength=self.zlength,
                      x=self.x_center,
                      y=self.y_center, z=self.z_center,
                      width=self.width, refractive_index=self.refractive_index, name="%s_arc%d" % (self.name, i + 1),
                      background_index=self.background_index, angle_psi=self.psi, angle_phi=self.phi)
            self._internal_objects.append(arc)
