from .waveguide import Waveguide
from . import sbend


class DirectionalCoupler(Waveguide):
    """方向耦合器，返回两个s波导的介电常数矩阵
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 中心坐标
    direction：确定方向 TODO: 完成竖直方向
    width：波导宽度
    refractive_index:折射率
    gap:直波导间距
    xlength_waveguide：直波导长度(耦合长度)"""

    # TODO 只需要输出两个s波导的矩阵，另外两个S波导的矩阵与他们一样，关键在于确定位置（未完成）
    def __init__(
        self,
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        direction=1,
        width=10,
        name="waveguide",
        refractive_index=1.7,
        xlength_rectangle=30,
        gap=5,
        background_index=1.0
    ):
        self.direction = direction
        self.xlength_rectangle = xlength_rectangle
        self.ylength_sbend = int((ylength - gap) / 2 + 0.5)
        self.xlength_sbend = int((xlength - xlength_rectangle) / 2 + 0.5)
        self.gap = gap
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index, background_index)

    def _set_objects(self):
        # permittivity_rectangle = 应该不用写矩形波导的介电常数？
        # 23.3.22: 由于器件不能重名，更改了下面name的表达式
        sbend1 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + int(self.xlength_sbend / 2),
            y=self.y + int(self.ylength_sbend / 2),
            z=self.z + int(self.zlength / 2),
            direction=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_sbend1" % self.name,
            background_index=self.background_index
        )

        sbend2 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + int(self.xlength_sbend / 2),
            y=self.y + int(self.gap + self.ylength_sbend * 1.5),
            z=self.z + int(self.zlength / 2),
            direction=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_sbend2" % self.name,
            background_index=self.background_index
        )

        sbend3 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + int(self.xlength_sbend * 1.5) + self.xlength_rectangle,
            y=self.y + int(self.gap + self.ylength_sbend * 1.5),
            z=self.z + int(self.zlength / 2),
            direction=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_sbend3" % self.name,
            background_index=self.background_index
        )

        sbend4 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + int(self.xlength_sbend * 1.5) + self.xlength_rectangle,
            y=self.y + int(self.ylength_sbend / 2),
            z=self.z + int(self.zlength / 2),
            direction=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_sbend4" % self.name,
            background_index=self.background_index
        )

        wg1 = Waveguide(
            xlength=self.xlength_rectangle,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend + int(self.xlength_rectangle / 2),
            y=self.y + self.ylength_sbend - int(self.width / 2),
            z=self.z + int(self.zlength / 2),
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_wg1" % self.name,
            background_index=self.background_index
        )

        wg2 = Waveguide(
            xlength=self.xlength_rectangle,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend + int(self.xlength_rectangle / 2),
            y=self.y + self.ylength_sbend + self.gap + int(self.width / 2),
            z=self.z + int(self.zlength / 2),
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_wg2" % self.name,
            background_index=self.background_index
        )

        self._internal_objects = [sbend1, sbend2, sbend3, sbend4, wg1, wg2]
