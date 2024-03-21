import numpy as np
from .arc import Arc


class FWG(Arc):
    """扇形波导光栅(fan-shaped waveguide grating)
    outer_radius: 外环半径
    ylength: 波导厚度
    x,y,z: 圆心坐标
    period: 光栅周期
    duty_cycle: 占空比
    number: number of periods 光栅周期数
    refractive_index:折射率
    name: 名称
    direction: 等于1，2，3，4，分别表示四个方向
    angle_phi: 与x轴正方向夹角, 单位: 角度
    angle_psi: 张角
    background_index: 环境折射率
    width: If period and duty_cycle have been set, width and gap will not be needed. 波导宽度
    gap: 缝宽
    """

    # TODO：现在只有x-y平面

    def __init__(
            self,
            outer_radius: int or float = 60,
            ylength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            period: int or float = None,
            duty_cycle: int or float = None,
            refractive_index: float = 3.47,
            name: str = "fwg",
            angle_phi: float = 0,
            angle_psi: float = 0,
            number: int = None,
            width: int or float = None,
            gap: int or float = None,
            grid=None
    ) -> None:

        # if not period or not duty_cycle:
        #     if not width or not gap:
        #         raise ValueError("Parameter 'period' and 'duty_cycle' of FWG must be set!")
        #     else:
        #         continue
        # TODO: FIXME: NOTE: python中赋值后面加逗号代表创建元组

        period, width, gap = grid._handle_unit([period, width, gap], grid_spacing=grid._grid.grid_spacing)
        if period and duty_cycle:
            if duty_cycle > 1:
                duty_cycle = 1
            if duty_cycle <= 0:
                raise ValueError("FWG's parameter duty_cycle must larger than 0.")
            width = int(np.round(period * duty_cycle))
            gap = period - width
        elif not width or not gap:
                raise ValueError("FWG's parameter 'period' and 'duty_cycle' have not been set yet.")

        self.gap = gap
        self.number = number

        super().__init__(outer_radius=outer_radius, ylength=ylength, x=x, y=y, z=z, width=width,
                         refractive_index=refractive_index, name=name, angle_phi=angle_phi, angle_psi=angle_psi,
                         grid=grid)

    def _set_objects(self):
        self._internal_objects = []
        for i in range(self.number):
            arc = Arc(outer_radius=self.outer_radius - (self.gap + self.width) * i, ylength=self.ylength,
                      x=self.x_center, y=self.y_center, z=self.z_center, width=self.width,
                      refractive_index=self.refractive_index, name="%s_arc%d" % (self.name, i + 1), angle_phi=self.phi,
                      angle_psi=self.psi, grid=self.grid)
            self._internal_objects.append(arc)

    def _compute_permittivity(self):
        """"""
