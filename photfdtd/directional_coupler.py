from .waveguide import Waveguide
from . import sbend
import fdtd


class DirectionalCoupler(Waveguide):
    """方向耦合器，返回两个s波导的介电常数矩阵
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    flag：参数
    width：波导宽度
    refractive_index:折射率
    gap:直波导间距
    xlength_rectangle：直波导长度(耦合长度)"""

    # TODO 只需要输出两个s波导的矩阵，另外两个S波导的矩阵与他们一样，关键在于确定位置（未完成）
    def __init__(
        self,
        xlength: int = 60,
        ylength: int = 10,
        zlength: int = 10,
        x: int = 50,
        y: int = 50,
        z: int = 50,
        direction: int = 1,
        width: int = 10,
        name: str = "waveguide",
        refractive_index: float = 1.7,
        xlength_rectangle: int = 30,
        gap: int = 5,
    ):
        self.direction = direction
        self.xlength_rectangle = xlength_rectangle
        self.ylength_sbend = int((ylength - gap) / 2 + 0.5)
        self.xlength_sbend = int((xlength - xlength_rectangle) / 2 + 0.5)
        self.gap = gap
        super().__init__(
            xlength, ylength, zlength, x, y, z, width, name, refractive_index
        )

    def _set_objects(self):
        # permittivity_rectangle = 应该不用写矩形波导的介电常数？
        # 左上波导sbend1
        sbend1 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            direction=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name=f"{self.name}_sbend1",
        )

        # 左下波导sbend2
        sbend2 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend + self.xlength_rectangle,
            y=self.y,
            z=self.z,
            direction=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name=f"{self.name}_sbend2",
        )

        # 右上波导sbend3
        sbend3 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x,
            y=self.y + self.ylength_sbend + self.gap,
            z=self.z,
            direction=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name=f"{self.name}_sbend3",
        )

        # 右下波导sbend4
        sbend4 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend + self.xlength_rectangle,
            y=self.y + self.ylength_sbend + self.gap,
            z=self.z,
            direction=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name=f"{self.name}_sbend4",
        )

        wg1 = Waveguide(
            xlength=self.xlength_rectangle,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend,
            y=self.y + self.ylength_sbend - self.width,
            z=self.z,
            width=self.width,
            refractive_index=self.refractive_index,
            name=f"{self.name}_wg1",
        )

        wg2 = Waveguide(
            xlength=self.xlength_rectangle,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend,
            y=self.y + self.ylength_sbend + self.gap,
            z=self.z,
            width=self.width,
            refractive_index=self.refractive_index,
            name=f"{self.name}_wg2",
        )

        self._internal_objects = [sbend1, sbend2, sbend3, sbend4, wg1, wg2]
