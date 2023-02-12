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
    ):
        self.direction = direction
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index)
        self.xlength_rectangle = xlength_rectangle
        self.ylength_sbend = int((ylength - gap) / 2 + 0.5)
        self.xlength_sbend = int((xlength - xlength_rectangle) / 2 + 0.5)
        self.gap = gap

    def set_grid(
        self,
        grid_xlength=175,
        grid_ylength=120,
        grid_zlength=1,
        grid_spacing=155e-9,
        total_time=1000,
        pml_width=5,
        permittivity=1**2,
    ):
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
            name="DC_sbend1",
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
            name="DC_sbend2",
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
            name="DC_sbend3",
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
            name="DC_sbend4",
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
            name="DC_wg1",
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
            name="DC_wg2",
        )

        grid = fdtd.Grid(
            shape=(grid_xlength, grid_ylength, grid_zlength), grid_spacing=grid_spacing, permittivity=permittivity
        )

        arr = [sbend1, sbend2, sbend3, sbend4, wg1, wg2]

        for i in range(6):
            grid[arr[i].x : arr[i].x + arr[i].xlength, arr[i].y : arr[i].y + arr[i].ylength] = fdtd.Object(
                permittivity=arr[i].permittivity, name=arr[i].name
            )

        grid[0:pml_width, :, :] = fdtd.PML(name="pml_xlow")
        grid[-pml_width:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
        grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")

        # 这一块光源代码应该拆出去
        grid[10:10, sbend1.y : sbend1.y + self.width] = fdtd.LineSource(
            period=1550e-9 / 299792458, name="source", pulse=True
        )

        self._total_time = total_time
        self._grid = grid
