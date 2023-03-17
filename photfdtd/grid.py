import fdtd
import matplotlib.pyplot as plt
from .waveguide import Waveguide


class Grid:
    def __init__(
        self, grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=0.01, total_time=1, pml_width=10
    ) -> None:
        """
        Args:
            grid_xlength (int, optional): _description_. Defaults to 100.
            grid_ylength (int, optional): _description_. Defaults to 200.
            grid_zlength (int, optional): _description_. Defaults to 50.
            grid_spacing (float, optional): fdtd算法的空间步长（yee元胞的网格宽度）. Defaults to 0.01.
            total_time (int, optional): 计算时间. Defaults to 1.
            pml_width (int, optional): PML宽度. Defaults to 10.
        """
        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength), grid_spacing=grid_spacing)

        grid[0:pml_width, :, :] = fdtd.PML(name="pml_xlow")
        grid[-pml_width:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
        grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")

        if grid_zlength != 1:
            grid[:, :, 0:pml_width] = fdtd.PML(name="pml_zlow")
            grid[:, :, -pml_width:] = fdtd.PML(name="pml_zhigh")

        self._grid_xlength = grid_xlength
        self._grid_ylength = grid_ylength
        self._grid_zlength = grid_zlength
        self._total_time = total_time
        self._grid = grid
        self._has_run = False

    def add_object(self, object: Waveguide):
        for internal_object in object._internal_objects:
            if internal_object.zlength != 1:
                self._grid[
                    internal_object.x : internal_object.x + internal_object.xlength,
                    internal_object.y : internal_object.y + internal_object.ylength,
                    internal_object.z : internal_object.z + internal_object.zlength,
                ] = fdtd.Object(permittivity=internal_object.permittivity, name=internal_object.name)
            else:
                self._grid[
                    internal_object.x : internal_object.x + internal_object.xlength,
                    internal_object.y : internal_object.y + internal_object.ylength,
                ] = fdtd.Object(permittivity=internal_object.permittivity, name=internal_object.name)

    def set_source(
        self,
        source_type: str = "pointsource",
        period: float = 15.0,
        amplitude: float = 1.0,
        phase_shift: float = 0.0,
        name: str = None,
        pulse: bool = False,
        cycle: int = 5,
        hanning_dt: float = 10.0,
        polarization: str = "z",
        x: int = 5,
        y: int = 5,
        z: int = 5,
        xlength: int = 5,
        ylength: int = 5,
        zlength: int = 5,
    ):
        """

        :param source_type: 光源种类：点或线或面
        :param period: 周期
        :param amplitude: 振幅
        :param phase_shift: 相移
        :param name: 名称
        :param pulse: 脉冲（默认为否）
        :param cycle: 脉冲周期
        :param hanning_dt: 汉宁窗宽度（定义脉冲）
        :param polarization: 偏振
        :param x:
        :param y:
        :param z:
        :param xlength:
        :param ylength:
        :param zlength:
        :return:
        """
        if source_type == "pointsource":
            # 创建一个点光源
            self._grid[x, y, z] = fdtd.PointSource(
                period=period,
                amplitude=amplitude,
                phase_shift=phase_shift,
                name=name,
                pulse=pulse,
                cycle=cycle,
                hanning_dt=hanning_dt,
            )

        elif source_type == "linesource":  # 创建一个线光源

            if self._grid_zlength == 1:
                self._grid[x : x + xlength, y : y + ylength] = fdtd.LineSource(
                    period=period,
                    amplitude=amplitude,
                    phase_shift=phase_shift,
                    name=name,
                    pulse=pulse,
                    cycle=cycle,
                    hanning_dt=hanning_dt,
                )
            else:
                self._grid[x : x + xlength, y : y + ylength, z : z + zlength] = fdtd.LineSource(
                    period=period,
                    amplitude=amplitude,
                    phase_shift=phase_shift,
                    name=name,
                    pulse=pulse,
                    cycle=cycle,
                    hanning_dt=hanning_dt,
                )

        elif source_type == "planesource":
            # 创建一个面光源
            self._grid[x : x + xlength, y : y + ylength, z : z + zlength] = fdtd.PlaneSource(
                period=period, amplitude=amplitude, phase_shift=phase_shift, name=name, polarization=polarization
            )

        else:
            raise RuntimeError("Invalid source type.")

    def savefig(self, filepath, axis="x"):
        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")

        if not self._has_run:
            self._grid.run(total_time=self._total_time)
            self._has_run = True

        axis = axis.lower()  # 识别大写的 "X", "Y", "Z"

        if axis == "x":  # 判断从哪一个轴俯视画图
            self._grid.visualize(x=0)
        elif axis == "y":
            self._grid.visualize(y=0)
        elif axis == "z":
            self._grid.visualize(z=0)
        else:
            raise RuntimeError("Unknown axis parameter.")

        plt.savefig(filepath)  # 保存图片
        plt.close()  # 清除画布
