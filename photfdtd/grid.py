import fdtd
import matplotlib.pyplot as plt
from .waveguide import Waveguide

import numpy as np
from numpy import savez
import os
from os import path, makedirs
from .analyse import Analyse
from .index import Index


class Grid:
    def __init__(
        self,
        grid_xlength: int = 100,
        grid_ylength: int = 200,
        grid_zlength: int = 50,
        grid_spacing: float = 0.01,  # TODO: raw中是0.001，疑似有误
        total_time: int = 1,
        pml_width_x=10,
        pml_width_y=10,
        pml_width_z=10,
        permittivity: float = 1.0,
        permeability: float = 1.0,
        courant_number: int = None,
    ) -> None:
        """
        Args:
            grid_xlength (int, optional): _description_. Defaults to 100.
            grid_ylength (int, optional): _description_. Defaults to 200.
            grid_zlength (int, optional): _description_. Defaults to 50.
            grid_spacing (float, optional): fdtd算法的空间步长（yee元胞的网格宽度）. Defaults to 0.01. （单位为米）
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

        grid[0:pml_width_x, :, :] = fdtd.PML(name="pml_xlow")
        grid[-pml_width_x:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:pml_width_y, :] = fdtd.PML(name="pml_ylow")
        grid[:, -pml_width_y:, :] = fdtd.PML(name="pml_yhigh")

        if pml_width_z != 0:
            grid[:, :, 0:pml_width_z] = fdtd.PML(name="pml_zlow")
            grid[:, :, -pml_width_z:] = fdtd.PML(name="pml_zhigh")

        self._grid_xlength = grid_xlength
        self._grid_ylength = grid_ylength
        self._grid_zlength = grid_zlength
        self._total_time = total_time
        self._grid = grid

    def add_object(self, object: Waveguide) -> None:
        for internal_object in object._internal_objects:
            self._grid[
                internal_object.x : internal_object.x + internal_object.xlength,
                internal_object.y : internal_object.y + internal_object.ylength,
                internal_object.z : internal_object.z + internal_object.zlength,
            ] = fdtd.Object(
                permittivity=internal_object.permittivity, name=internal_object.name
            )

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
    ) -> None:
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
                self._grid[
                    x : x + xlength, y : y + ylength, z : z + zlength
                ] = fdtd.LineSource(
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
            self._grid[
                x : x + xlength, y : y + ylength, z : z + zlength
            ] = fdtd.PlaneSource(
                period=period,
                amplitude=amplitude,
                phase_shift=phase_shift,
                name=name,
                polarization=polarization,
            )

        else:
            raise RuntimeError("Invalid source type.")

    def set_detector(
        self,
        detector_type: str = "linedetector",
        x: int = 0,
        y: int = 0,
        z: int = 0,
        xlength: int = 0,
        ylength: int = 0,
        zlength: int = 0,
        name: str = "detector",
    ):
        # 设置监视器
        if detector_type == "linedetector":
            self._grid[
                x : x + xlength, y : y + ylength, z : z + zlength
            ] = fdtd.LineDetector(name=name)

        elif detector_type == "blockdetector":
            self._grid[
                x : x + xlength, y : y + ylength, z : z + zlength
            ] = fdtd.BlockDetector(name=name)
        else:
            raise RuntimeError("Invalid detector type.")

    def savefig(  # TODO: 保存图片，详细参数需要进一步对接，比如是否需要Folder？
        self, filepath: str, x: int = None, y: int = None, z: int = None
    ) -> None:
        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")
        # 不设置 save 参数，因为 visualize 把路径设置死了，不好修改，选择在外面调用 plt.savefig()
        self._grid.visualize(
            x=x, y=y, z=z, index=f"_(x={x},y={y},z={z}), total_time={self._total_time}"
        )

        plt.savefig(filepath)  # 保存图片
        plt.clf()  # 清除画布

    def run(self) -> None:
        if self._grid is None:
            raise RuntimeError("The grid should be set before running.")

        self._grid.run(total_time=self._total_time)

    def save_simulation(self, filename: str = "test"):
        """保存监视器数据。
        调用了fdtd库的grid.save_simulation函数, 会在当前目录下新建一个fdtd_output文件夹，在里面新建名称为fdtd_output_2023-4-3-15-27-58 (filename)的文件夹
        ，在其中创建detector_readings.npz来保存监视器数据"""
        self._grid.save_simulation(filename)
        self._grid.save_data()

    def read_simulation(self, filepath: str = ""):
        """读取保存的监视器数据
        filepath: 保存监视器数据的文件路径（即save_simulation中创建的detector_readings.npz）
        例："D:/下载内容/photfdtd-main/tests/fdtd_output/fdtd_output_2023-4-3-15-27-58 (test0403)/detector_readings.npz "
        """
        readings = np.load(filepath, allow_pickle=True)
        self.detector_E, self.detector_H = np.zeros(len(self._grid.detectors))
        for i in range(len(self._grid.detectors)):
            self.detector_E[i], self.detector_H[i] = (
                readings["%s (E)" % self._grid.detectors[i].name],
                readings["%s (H)" % self._grid.detectors[i].name],
            )

    def calulate_T(self) -> None:
        """
        读取detector_readings_sweep.npz文件，计算透过率T
        """
        # 只能设置一个除光源
        p = np.load(self.full_path, allow_pickle=True)
        # 遍历.npz文件中的所有数据，若为监视器数据（即带有(E)或(H)), 则读取之

        for f in p.files:
            # 遍历detector_readings_sweep.npz中的所有数据
            if "source" in f:
                # 筛选出光源监视器
                if "(E)" in f:
                    d_E = p["%s" % f]
                elif "(H)" in f:
                    d_H = p["%s" % f]

        d_E_split = np.split(d_E, self.points, axis=0)  # 沿着第0个轴分割为points个小矩阵
        d_H_split = np.split(d_H, self.points, axis=0)  # 沿着第0个轴分割为points个小矩阵
        # ！！！这样写只能设置一个光源，也只能设置一个除光源外的监视器，并且光源处的监视器名称必须含有"source"！！！

        source_power = []
        for i in range(len(d_E_split)):
            # 计算光源功率
            calculate = Analyse(d_E_split[i], d_H_split[i])
            calculate.caculate_P()
            calculate.calculate_Power()
            source_power.append(calculate.Power)

        detector_power = []
        for f in p.files:
            if "source" in f:
                continue
            elif "(E)" in f:
                d_E = p["%s" % f]
                continue
            elif "(H)" in f:
                # 能这样写是因为E保存在H之前
                d_H = p["%s" % f]
                # 沿着第0个轴分割为points个小矩阵
                d_E_split = np.split(d_E, self.points, axis=0)
                # 沿着第0个轴分割为points个小矩阵
                d_H_split = np.split(d_H, self.points, axis=0)
                for i in range(len(d_E_split)):
                    calculate = Analyse(d_E_split[i], d_H_split[i])
                    calculate.caculate_P()
                    calculate.calculate_Power()
                    detector_power.append(calculate.Power)

                continue
            else:
                continue

        # 在self.T中保存透过率, 即监视器与光源功率相除
        self.T = np.divide(detector_power, source_power)

    def _sweep_( #TODO: 有个e未定义？
        self,
        wl_start: float = 1.5,
        wl_end: float = 1.6,
        points: int = 100,
        folder: str = "",
        material: str = "",
    ) -> None:
        """
        频率扫描
        :param folder: 保存文件夹名。先创建"fdtd_output"文件夹，然后在里面创建"fdtd_output_" + folder文件夹
        :param material: 材料
        :param wl_start: 起始波长
        :param wl_end: 结束波长
        :param points: 计算点数
        """
        # 读取折射率数据。把文件路径替换为保存折射率数据的路径
        # TODO: 改为自动识别object的材料并修改折射率
        index = Index("D:/下载内容/photfdtd-main/photfdtd/折射率数据/%s.csv" % material)
        index._fit_()

        # 创建保存文件夹
        self.wl_start = wl_start
        self.wl_end = wl_end
        self.points = points
        makedirs("fdtd_output", exist_ok=True)
        folder = "fdtd_output_" + folder
        # 在fdtd_output文件夹下创建文件夹，
        self.folder = os.path.abspath(path.join("fdtd_output", folder))
        makedirs(self.folder, exist_ok=True)
        for wl in np.linspace(wl_start, wl_end, points):
            for attr in dir(self._grid):
                # 遍历grid的所有属性
                try:
                    if isinstance(getattr(self._grid, attr), fdtd.Object):
                        # 找到Object类型的属性并修改permittivity属性
                        getattr(self._grid, attr).permittivity[
                            getattr(self._grid, attr).permittivity != 1
                        ] = np.square(index.fit_function_Reindex(wl))
                        # inverse_permittivity: 逆电容率（介电常数），即permittivity的倒数
                        getattr(self._grid, attr).inverse_permittivity[
                            getattr(self._grid, attr).inverse_permittivity != 1
                        ] = 1 / np.square(index.fit_function_Reindex(wl))
                    if (
                        isinstance(getattr(self._grid, attr), fdtd.PointSource)
                        or isinstance(getattr(self._grid, attr), fdtd.LineSource)
                        or isinstance(getattr(self._grid, attr), fdtd.PlaneSource)
                    ):
                        # 找到光源，修改波长
                        getattr(self._grid, attr).period = wl * e - 9 / 299792458
                except:
                    pass
            # reset()这个函数很重要，如果没有这个函数，会接着之前的时间往下run
            self._grid.reset()
            self.run()

        dic = {}

        # reset()函数清空了E，H和时间，但是在reset之后，监视器记录的数据不会清零，而是继续记录下去，所以只需保留最后一个监视器数据，然后切片就行
        # TODO: 这样会占用大量内存，能不能修改？但是修改可能需要改fdtd包
        for detector in self._grid.detectors:
            dic[detector.name + " (E)"] = [x for x in detector.detector_values()["E"]]
            dic[detector.name + " (H)"] = [x for x in detector.detector_values()["H"]]
        # 保存detector_readings_sweep.npz文件
        savez(path.join(self.folder, "detector_readings_sweep"), **dic)

    def _plot_sweep_result(self):
        for file_name in os.listdir(self.folder):
            if file_name.endswith("_sweep.npz"):
                # 识别_sweep.npz文件
                self.full_path = os.path.join(self.folder, file_name)
                self.calulate_T()
        print(self.T)

        x = np.linspace(self.wl_start, self.wl_end, self.points)

        # TODO: 除了光源监视器外只能设置一个监视器，只能看一个端口的透过率，完善它。
        plt.plot(x, self.T)
        plt.xlabel("Wavelength (μm)")
        plt.ylabel("T")
        plt.savefig(fname="%s//wl-%s.png" % (self.folder, "T"))
        plt.show()
