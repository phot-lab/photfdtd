import fdtd
import matplotlib.pyplot as plt
from .waveguide import Waveguide


class Grid:
    def __init__(
        self,
        grid_xlength: int = 100,
        grid_ylength: int = 200,
        grid_zlength: int = 50,
        grid_spacing: float = 0.01,
        total_time: int = 1,
        pml_width: int = 10,
        permittivity: float = 1.0,
        permeability: float = 1.0,
        courant_number: int = None,
    ) -> None:
        """
        Args:
            grid_xlength (int, optional): _description_. Defaults to 100.
            grid_ylength (int, optional): _description_. Defaults to 200.
            grid_zlength (int, optional): _description_. Defaults to 50.
            grid_spacing (float, optional): fdtd算法的空间步长（yee元胞的网格宽度）. Defaults to 0.01.
            total_time (int, optional): 计算时间. Defaults to 1.
            pml_width (int, optional): PML宽度. Defaults to 10.
            permeability (float, optional): 环境磁导率 1.0
            permittivity (float, optional): 环境介电常数，二者共同决定了环境折射率 1.0
            courant_number: 科朗数 默认为None
        """
        grid = fdtd.Grid(
            shape=(grid_xlength, grid_ylength, grid_zlength),
            grid_spacing=grid_spacing,
            permittivity=permittivity,
            permeability=permeability,
            courant_number=courant_number,
        )

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

    def savefig(self, filepath: str, x: int = None, y: int = None, z: int = None):
        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")

        if not self._has_run:
            self._grid.run(total_time=self._total_time)
            self._has_run = True

        # 不设置 save 参数，因为 visualize 把路径设置死了，不好修改，选择在外面调用 plt.savefig()
        self._grid.visualize(x=x, y=y, z=z)

        plt.savefig(filepath)  # 保存图片
        plt.clf()  # 清除画布
