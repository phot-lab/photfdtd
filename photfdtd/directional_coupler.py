from .waveguide import Waveguide
from . import sbend


class DirectionalCoupler(Waveguide):
    """方向耦合器，返回两个s波导的介电常数矩阵
    ylength: 波导区域y方向宽度
    x,y,z: 中心坐标
    width_1: 波导1宽度
    width_2: 波导2宽度
    refractive_index:折射率
    gap:直波导间距
    zlength_rectangle：直波导长度(耦合长度)
    zlength_sbend: Sbend z方向长度,
    xlength_sbend: Sbend x方向长度,
    background_index：环境折射率
    在设置以上参数后，以下参数可以不设置：
        xlength: 波导区域x方向宽度
        zlength: 波导区域厚度
    priority: the priority of the waveguide( high index indicates high priority).
    """

    def __init__(
        self,
            xlength: int or float = 200,
            ylength: int or float = 80,
            zlength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width_1: int or float = 20,
            width_2: int or float = None,
            name: str = "dc",
            refractive_index: float = 3.47,
            zlength_rectangle: int or float = 50,
            zlength_sbend: int or float = None,
            xlength_sbend: int or float = None,
            gap: int or float = 10,
            grid=None,
            priority: int = 1
    ) -> None:
        if not width_2:
            width_2 = width_1
        xlength, ylength, zlength, width_1, width_2, zlength_rectangle, gap, zlength_sbend, xlength_sbend = \
            grid._handle_unit([xlength, ylength, zlength, width_1, width_2, zlength_rectangle, gap, zlength_sbend, xlength_sbend],
                                                                                     grid_spacing=grid._grid.grid_spacing)
        self.zlength_rectangle = zlength_rectangle
        if xlength_sbend is not None:
            self.xlength_sbend = xlength_sbend
            xlength = self.xlength_sbend * 2 + gap
        else:
            self.xlength_sbend = int((xlength - gap) / 2 + 0.5)
        if zlength_sbend is not None:
            self.zlength_sbend = zlength_sbend
            zlength = self.zlength_sbend * 2 + self.zlength_rectangle
        else:
            self.zlength_sbend = int((zlength - zlength_rectangle) / 2 + 0.5)
        self.gap = gap
        self.width_2 = width_2
        super().__init__(xlength=xlength, ylength=ylength, zlength=zlength, x=x, y=y, z=z, width=width_1,
                         name=name, refractive_index=refractive_index, grid=grid, priority=priority)

    def _set_objects(self):
        sbend1 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength,
            zlength=self.zlength_sbend,
            x=self.x + int(self.xlength_sbend / 2),
            y=self.y + int(self.ylength / 2),
            z=self.z + int(self.zlength_sbend / 2),
            direction=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_sbend1" % self.name,
            grid=self.grid,
            center_postion=True,
            priority=self.priority
        )

        sbend2 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength,
            zlength=self.zlength_sbend,
            x=self.x + int(self.gap + self.xlength_sbend * 1.5),
            y=self.y + int(self.ylength / 2),
            z=self.z + int(self.zlength_sbend / 2),
            direction=-1,
            width=self.width_2,
            refractive_index=self.refractive_index,
            name="%s_sbend2" % self.name,
            grid=self.grid,
            center_postion=True,
            priority=self.priority
        )

        sbend3 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength,
            zlength=self.zlength_sbend,
            x=self.x + int(self.gap + self.xlength_sbend * 1.5),
            y=self.y + int(self.ylength / 2),
            z=self.z + int(self.zlength_sbend * 1.5) + self.zlength_rectangle,
            direction=1,
            width=self.width_2,
            refractive_index=self.refractive_index,
            name="%s_sbend3" % self.name,
            grid=self.grid,
            center_postion=True,
            priority=self.priority
        )

        sbend4 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength,
            zlength=self.zlength_sbend,
            x=self.x + int(self.xlength_sbend / 2),
            y=self.y + int(self.ylength / 2),
            z=self.z + int(self.zlength_sbend * 1.5) + self.zlength_rectangle,
            direction=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_sbend4" % self.name,
            grid=self.grid,
            center_postion=True,
            priority=self.priority
        )
        self.zlength_rectangle += 2  # +4防止出现空隙
        wg1 = Waveguide(
            xlength=self.width,
            ylength=self.ylength,
            zlength=self.zlength_rectangle,
            x=self.x + self.xlength_sbend - int(self.width / 2),
            y=self.y_center,
            z=self.z_center,
            refractive_index=self.refractive_index,
            name="%s_wg1" % self.name,
            grid=self.grid,
            priority=self.priority
        )

        wg2 = Waveguide(
            xlength=self.width_2,
            ylength=self.ylength,
            zlength=self.zlength_rectangle,
            x=self.x + self.xlength_sbend + self.gap + int(self.width_2 / 2),
            y=self.y_center,
            z=self.z_center,
            refractive_index=self.refractive_index,
            name="%s_wg2" % self.name,
            grid=self.grid,
            priority=self.priority
        )

        self._internal_objects = [sbend1, sbend2, sbend3, sbend4, wg1, wg2]
