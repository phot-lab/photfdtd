import photfdtd.fdtd as fdtd
import matplotlib.pyplot as plt
from .waveguide import Waveguide
import numpy as np
from datetime import datetime
from numpy import savez
import os
from os import path, makedirs, chdir, remove
from .analyse import Analyse
from .index import Index
from photfdtd import constants


class Grid:

    def __init__(
            self, grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=20e-9, total_time=1, pml_width_x=10,
            pml_width_y=10, pml_width_z=0, permittivity=1.0, permeability=1.0, courant_number=None, foldername=" ",
            folder=None
    ) -> None:
        """
        Args:
            grid_xlength (int, optional): _description_. Defaults to 100.
            grid_ylength (int, optional): _description_. Defaults to 200.
            grid_zlength (int, optional): _description_. Defaults to 50.
            grid_spacing (float, optional): fdtd算法的空间步长（yee元胞的网格宽度）. 单位为m
            total_time (int, optional): 计算时间. Defaults to 1.
            pml_width (int, optional): PML宽度.
            permeability (float, optional): 环境相对磁导率 1.0
            permittivity (float, optional): 环境相对介电常数，二者共同决定了环境折射率 1.0
            (refractive_index ** 2 = permeability * permittivity, 对大部分材料permeability=1.0)
            courant_number: 科朗数 默认为None
            foldername: 文件夹名称, 若其不存在将在目录下创建该文件夹
        """
        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength),
                         grid_spacing=grid_spacing,
                         permittivity=permittivity,
                         permeability=permeability,
                         courant_number=courant_number
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

        # makedirs(foldername, exist_ok=True)  # Output master folder declaration
        current_dir = os.getcwd()

        # self.folder: 保存结果的文件夹
        self.folder = os.path.join(current_dir, foldername)
        if folder != "" and folder is not None:
            self.folder = folder
        makedirs(self.folder, exist_ok=True)

        self.background_index = np.sqrt(permittivity * permeability)

    def add_object(self, object: Waveguide):

        for internal_object in object._internal_objects:
            # 23.04.14: 删去了不必要的判断语句
            if internal_object == 0:
                continue
            else:
                self._grid[
                internal_object.x: internal_object.x + internal_object.xlength,
                internal_object.y: internal_object.y + internal_object.ylength,
                internal_object.z: internal_object.z + internal_object.zlength,
                ] = fdtd.Object(permittivity=internal_object.permittivity, name=internal_object.name)

    def set_source(
            self,
            source_type: str = "pointsource",
            wavelength=None,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            name: str = "source",
            waveform: str = "plane",
            pulse_type: str = "none",
            cycle: int = 5,
            hanning_dt: float = 10.0,
            polarization: str = "z",
            pulse_length: float = 39e-15,
            offset: float = 112e-15,
            x: int = 5,
            y: int = 5,
            z: int = 5,
            xlength: int = 5,
            ylength: int = 5,
            zlength: int = 5,
    ):
        """
        编辑于23.5.15 加入pulse_type: str = "gaussian",  pulse_length: float = 39e-15,offset: float = 112e-15,
        :param source_type: 光源种类：点或线或面
        :param wavelength: 波长(m)
        :param amplitude: 振幅(V/m)
        :param phase_shift: 相移
        :param name: 名称
        :param waveform: 波形 "plane":平面波 "gaussian": 高斯波
        :param cycle: 汉宁窗脉冲的周期（仅使用汉宁hanning脉冲时有用）
        :param hanning_dt: 汉宁窗宽度（仅使用汉宁hanning脉冲时有用）
        :param polarization: 偏振
        :param pulse_length:脉宽(s)
        :param pulse_type: 脉冲类型 "gaussian" 或 "hanning" 或 "none"
        :param offset: 脉冲中心(s)
        :param x: 位置坐标（中心）
        :param y:
        :param z:
        :param xlength:
        :param ylength:
        :param zlength:
        """
        if wavelength != None:
            period = wavelength / constants.c

        x = x - xlength // 2
        y = y - ylength // 2
        z = z - zlength // 2
        if source_type == "pointsource":
            # 创建一个点光源
            x = x + xlength // 2
            y = y + ylength // 2
            z = z + zlength // 2

            self._grid[x, y, z] = fdtd.PointSource(period=period, amplitude=amplitude, phase_shift=phase_shift,
                                                   name=name, cycle=cycle, hanning_dt=hanning_dt, pulse_type=pulse_type,
                                                   pulse_length=pulse_length, offset=offset, polarization=polarization)

        elif source_type == "linesource":  # 创建一个线光源

            if self._grid_zlength == 1:
                self._grid[x: x + xlength, y: y + ylength] = fdtd.LineSource(period=period, amplitude=amplitude,
                                                                             phase_shift=phase_shift, name=name,
                                                                             pulse_type=pulse_type, cycle=cycle,
                                                                             pulse_length=pulse_length, offset=offset,
                                                                             waveform=waveform, polarization=polarization)
            else:
                self._grid[x: x + xlength, y: y + ylength, z: z + zlength] = fdtd.LineSource(period=period,
                                                                                             amplitude=amplitude,
                                                                                             phase_shift=phase_shift,
                                                                                             name=name,
                                                                                             pulse_type=pulse_type,
                                                                                             cycle=cycle,
                                                                                             pulse_length=pulse_length,
                                                                                             offset=offset,
                                                                                             waveform=waveform,
                                                                                             polarization=polarization)

        elif source_type == "planesource":
            # 创建一个面光源
            self._grid[x: x + xlength, y: y + ylength, z: z + zlength] = fdtd.PlaneSource(
                period=period, amplitude=amplitude, phase_shift=phase_shift, name=name, polarization=polarization
            )

        else:
            raise RuntimeError("Invalid source type.")

    def set_detector(self,
                     detector_type: str = 'linedetector',
                     x: int = 5,
                     y: int = 5,
                     z: int = 5,
                     xlength: int = 5,
                     ylength: int = 5,
                     zlength: int = 1,
                     name: str = 'detector'
                     ):
        x = x - xlength // 2
        y = y - ylength // 2
        z = z - zlength // 2
        # 设置监视器
        if detector_type == 'linedetector':
            self._grid[x: x + xlength,
            y: y + ylength,
            z: z + zlength] = fdtd.LineDetector(name=name)

        elif detector_type == 'blockdetector':
            self._grid[x: x + xlength,
            y: y + ylength,
            z: z + zlength] = fdtd.BlockDetector(name=name)
        else:
            raise RuntimeError("Invalid detector type.")

    def save_fig(self,
                 axis="x",
                 axis_number=0,
                 animate=False,
                 time=None):
        """
        保存图片
        @param axis: 轴(若为二维模拟，则axis只能='z')
        @param axis_number: 索引
        @param time: 绘制哪个时刻的场图（用户用不到，仅供run()使用
        @param animate: 是否播放动画 #TODO: 这个参数的作用？
        :
        """
        # TODO: grid.visualize函数还有animate等功能，尚待加入
        if time == None:
            time = self._total_time
        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")

        axis = axis.lower()  # 识别大写的 "X"
        folder = self.folder
        if axis == "x":  # 绘制截面/剖面场图
            self._grid.visualize(x=axis_number, save=True, animate=animate,
                                 index="_%s=%d, total_time=%d" % (axis, axis_number, time), folder=folder)
        elif axis == "y":
            self._grid.visualize(y=axis_number, save=True, animate=animate,
                                 index="_%s=%d, total_time=%d" % (axis, axis_number, time), folder=folder)
        elif axis == "z":
            self._grid.visualize(z=axis_number, save=True, animate=animate,
                                 index="_%s=%d, total_time=%d" % (axis, axis_number, time), folder=folder)
        else:
            raise RuntimeError("Unknown axis parameter.")

        plt.close()  # 清除画布

    def run(self,
            animate: bool = False,
            step: int = 5,
            axis="x",
            axis_number=0,
            ):
        """

        @param axis: 与save_fig()相同
        @param axis_number:
        @param animate: 是否播放动画 %TODO: 完成它
        @param step: 每多少个时间步绘一次图
        """
        axis = axis.lower()
        if animate == False:
            self._grid.run(total_time=self._total_time)
        elif animate:
            for i in range(self._total_time):
                self._grid.step()
                if (i + 1) % step == 0:
                    if axis == "x":
                        self.visualize(x=axis_number, showEnergy=True, show=False, save=True, time=i)
                    elif axis == "y":
                        self.visualize(y=axis_number, showEnergy=True, show=False, save=True, time=i)
                    elif axis == "z":
                        self.visualize(z=axis_number, showEnergy=True, show=False, save=True, time=i)
                    else:
                        continue

    def animate(self,
                axis: str = "z",
                number: int = 0):
        # TODO: 完成它，让正则表达式能识别完整地址
        import re
        from PIL import Image
        import imageio

        # 文件夹路径
        folder_path = self.folder

        # 用户定义的 "z" 字符串和 "z=" 后面的数字
        z_str = "z"  # 用户定义的 "z" 字符串
        z_equals_value = 0  # 用户定义的 "z=" 后面的数字

        # 定义正则表达式模式，匹配文件名中的 "file_z=" 和 "total_time=" 后面的数字
        pattern = re.compile(fr'file_{z_str}={z_equals_value}, total_time=(\d+).png')

        # 获取文件夹中所有图片文件
        image_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]

        # 过滤出满足用户定义条件的图片文件，并按 "total_time" 后面的数字从大到小排序
        # filtered_images = sorted([file for file in image_files if pattern.match(file)],
        #                          key=lambda x: int(pattern.match(x).group(1)), reverse=True)
        filtered_images = sorted([file for file in image_files if pattern.match(os.path.basename(file))],
                                 key=lambda x: int(pattern.match(x).group(1)), reverse=True)

        print(self.folder)
        print(filtered_images)
        # 创建一个图像列表
        images = []

        # 逐个读取筛选后的图片文件并添加到图像列表中
        for file_path in filtered_images:
            img = imageio.imread(file_path)
            images.append(img)

        output_file = 'output_animation.mp4'

        # 使用 get_writer() 函数创建视频写入对象，设置帧之间的持续时间（秒）
        with imageio.get_writer(output_file, fps=10) as writer:
            for img in images:
                writer.append_data(img)

        print(f'动画已保存为 {output_file}')

    def calculate_T(self,
                    full_path: str = "") -> None:
        """
        读取detector_readings_sweep.npz文件，计算透过率T
        full_path: npz文件的完整地址
        """
        # 只能设置一个除光源
        pass
        # TODO: 这个函数需要大改
        p = np.load(full_path, allow_pickle=True)
        # 遍历.npz文件中的所有数据，若为监视器数据（即带有(E)或(H)), 则读取之
        source_power = []

        for f in p.files:
            # 遍历detector_readings_sweep.npz中的所有数据
            # 这样写只能设置一个光源，也只能设置一个除光源外的监视器，并且光源处的监视器名称必须含有"source"
            if "source" in f:
                # 筛选出光源监视器
                # print(p[f])
                if "(E)" in f:
                    d_E = p[f]
                    continue
                elif "(H)" in f:
                    d_H = p[f]
                calculate = Analyse(d_E, d_H)
                calculate.caculate_P()
                calculate.calculate_Power()
                source_power.append(calculate.Power)
                print("source_power = %f" % calculate.Power)

        detector_power = []
        for f in p.files:
            if "source" in f:
                continue
            elif "(E)" in f:
                d_E = p['%s' % f]
                continue
            elif "(H)" in f:
                # 能这样写是因为E保存在H之前
                d_H = p['%s' % f]
                # d_E_split = np.split(d_E, self.points, axis=0)  # 沿着第0个轴分割为points个小矩阵
                # d_H_split = np.split(d_H, self.points, axis=0)  # 沿着第0个轴分割为points个小矩阵
            calculate = Analyse(d_E, d_H)
            calculate.caculate_P()
            calculate.calculate_Power()
            detector_power.append(calculate.Power)
            print("detector_power = %f" % calculate.Power)

        # 在self.T中保存透过率, 即监视器与光源功率相除
        self.T = np.divide(detector_power, source_power)

    def _sweep_(self,
                wl_start: float = 1.5,
                wl_end: float = 1.6,
                points: int = 100,
                material: str = "") -> None:
        """
        #TODO: 这个函数需要重写
        频率扫描
        :param material: 材料
        :param wl_start: 起始波长
        :param wl_end: 结束波长
        :param points: 计算点数
        """
        # 读取折射率数据。把文件路径替换为保存折射率数据的路径
        # TODO: 改为自动识别object的材料并修改折射率
        pass
        index = Index('D:/下载内容/photfdtd-main/photfdtd/折射率数据/%s.csv' % material)
        index._fit_()

        # 创建保存文件夹
        self.wl_start = wl_start
        self.wl_end = wl_end
        self.points = points
        # makedirs("fdtd_output", exist_ok=True)
        # folder = "fdtd_output_" + folder
        # # 在fdtd_output文件夹下创建文件夹，
        # self.folder = os.path.abspath(path.join("fdtd_output", folder))
        # makedirs(self.folder, exist_ok=True)
        dic = {}
        for wl in np.linspace(wl_start, wl_end, points):
            for attr in dir(self._grid):
                # 遍历grid的所有属性
                try:
                    if isinstance(getattr(self._grid, attr), fdtd.Object):
                        # 找到Object类型的属性并修改permittivity属性
                        getattr(self._grid, attr).permittivity[
                            getattr(self._grid, attr).permittivity != 1] = np.square(index.fit_function_Reindex(wl))
                        # inverse_permittivity: 逆电容率（介电常数），即permittivity的倒数
                        getattr(self._grid, attr).inverse_permittivity[
                            getattr(self._grid, attr).inverse_permittivity != 1] = 1 / np.square(
                            index.fit_function_Reindex(wl))
                        # print("已修改object")
                    else:
                        continue
                except:
                    continue
            for i in range(len(self._grid.sources)):
                # 修改光波长
                self._grid.sources[i].period = self._grid._handle_time(wl * 10 ** -6 / 299792458)
                # print("已修改source")

            self.run()

            # TODO: 面监视与点监视器
            # 保存监视器数据
            for detector in self._grid.detectors:
                dic[detector.name + " (E)" + " %f" % wl] = [x for x in detector.detector_values()["E"]]
                dic[detector.name + " (H)" + " %f" % wl] = [x for x in detector.detector_values()["H"]]
                detector.E = []
                detector.H = []
            # for attr in dir(self._grid):
            #     # 遍历grid的所有属性
            #     try:
            #         if isinstance(getattr(self._grid, attr), fdtd.LineDetector):
            #             # 找到 LineDetectr 类型的属性并设置E与H场=0
            #             getattr(self._grid, attr).E = []
            #             getattr(self._grid, attr).H = []
            #     except:
            #         pass
            # 重置grid
            self._grid.reset()

        # 保存detector_readings_sweep.npz文件
        savez(path.join(self.folder, "detector_readings_sweep"), **dic)

    def _plot_sweep_result(self,
                           folder: str = ""):
        pass
        # TODO: 完成它
        if folder == "":
            folder = self.folder

        for file_name in os.listdir(folder):
            if file_name.endswith('_sweep.npz'):
                # 识别_sweep.npz文件
                # self.full_path = os.path.join(self.folder, file_name)
                self.calculate_T(full_path=os.path.join(folder, file_name))
        print(self.T)

        x = np.linspace(self.wl_start, self.wl_end, self.points)

        # TODO: 除了光源监视器外只能设置一个监视器，只能看一个端口的透过率，完善它。
        plt.plot(x, self.T)
        plt.xlabel('Wavelength (μm)')
        plt.ylabel("T")
        plt.savefig(fname='%s//wl-%s.png' % (self.folder, "T"))
        plt.show()

    # 保存数据
    def save_simulation(self):
        dic = {}
        for detector in self._grid.detectors:
            dic[detector.name + " (E)"] = [x for x in detector.detector_values()["E"]]
            dic[detector.name + " (H)"] = [x for x in detector.detector_values()["H"]]
        dic["grid_spacing"] = self._grid.grid_spacing
        dic["time_step"] = self._grid.time_step
        dic["detectors"] = self._grid.detectors
        dic["sources"] = self._grid.sources
        dic["time_passed"] = self._grid.time_passed

        # 保存detector_readings_sweep.npz文件
        savez(path.join(self.folder, "detector_readings"), **dic)

    @staticmethod
    def read_simulation(folder: str = ''):
        """读取保存的监视器数据
        静态方法，调用时应使用 data = Grid.read_simulation(folder="...")
        folder: 保存监视器数据的文件路径
        """
        # TODO: 将结果绘图
        if not folder.endswith(".npz"):
            folder = folder + "/detector_readings.npz"

        readings = np.load(folder, allow_pickle=True)
        names = readings.files
        data = {}
        i = 0
        for name in names:
            data[name] = readings[name]
            i += 1

        return data

    def compute_frequency_domain(self, wl_start, wl_end, input_data):
        # TODO: fdtd原作者想要让这里的输入为监视器，但是他并没有完成这一代码，现在只能输入一维数据，完成它?
        # TODO: 傅里叶变换后的单位？
        fr = fdtd.FrequencyRoutines(self._grid, objs=input_data)
        spectrum_freqs, spectrum = fr.FFT(
            freq_window_tuple=[299792458 / (wl_end * (10 ** -6)), 299792458 / (wl_start * (10 ** -6))], )

        # 绘制频谱
        plt.plot(spectrum_freqs, spectrum)
        plt.xlabel('frequency (Hz)')
        plt.ylabel("spectrum")
        plt.savefig(fname='%s//f-spectrum_time=%i.png.png' % (self.folder, self._total_time))
        plt.close()

        # 绘制频率-振幅
        plt.plot(spectrum_freqs, np.abs(spectrum))
        plt.xlabel('frequency (Hz)')
        plt.ylabel("amplitude")
        plt.savefig(fname='%s//f-amplitude_time=%i.png.png' % (self.folder, self._total_time))
        plt.close()

        # 绘制频率-相位
        plt.plot(299792458 / (spectrum_freqs * (10 ** -6)), np.abs(spectrum))
        plt.xlabel('wavelength (um)')
        plt.ylabel("amplitude")
        plt.savefig(fname='%s//wl-amplitude_time=%i.png' % (self.folder, self._total_time))
        plt.close()

        # 绘制波长-透过率
        # x = np.linspace(wl_start, wl_end, points)
        # plt.plot(x, T)
        # plt.xlabel('Wavelength (μm)')
        # plt.ylabel("T")
        # plt.savefig(fname='%s//wl-T_time=%i.png' % (grid.folder, grid._total_time))
        # print(T)

    def visualize(
            self,
            x=None,
            y=None,
            z=None,
            cmap="Blues",
            pbcolor="C3",
            pmlcolor=(0, 0, 0, 0.1),
            objcolor=(1, 0, 0, 0.1),
            srccolor="C0",
            detcolor="C2",
            norm="linear",
            showEnergy=True,
            legend=False,
            show=False,  # default False to allow animate to be true
            save=False,  # True to save frames (requires parameters index, folder)
            filePath=None,
            time=None
    ):
        """visualize a projection of the grid and the optical energy inside the grid

        Args:
            x: the x-value to make the yz-projection (leave None if using different projection)
            y: the y-value to make the zx-projection (leave None if using different projection)
            z: the z-value to make the xy-projection (leave None if using different projection)
            cmap: the colormap to visualize the energy in the grid
            pbcolor: the color to visualize the periodic boundaries
            pmlcolor: the color to visualize the PML
            objcolor: the color to visualize the objects in the grid
            srccolor: the color to visualize the sources in the grid
            detcolor: the color to visualize the detectors in the grid
            norm: how to normalize the grid_energy color map ('linear' or 'log').
            show: call pyplot.show() at the end of the function
            save: save frames in a folder
            folder: path to folder to save frames
            showEnergy: 是否显示场
        """
        if norm not in ("linear", "lin", "log"):
            raise ValueError("Color map normalization should be 'linear' or 'log'.")
        # imports (placed here to circumvent circular imports)
        import matplotlib.pyplot as plt
        import matplotlib.patches as ptc
        from matplotlib.colors import LogNorm
        # relative
        from .fdtd.backend import backend as bd
        from .fdtd.sources import PointSource, LineSource, PlaneSource
        # from fdtd.boundaries import _PeriodicBoundaryX, _PeriodicBoundaryY, _PeriodicBoundaryZ
        # from fdtd.boundaries import (
        #     _PMLXlow,
        #     _PMLXhigh,
        #     _PMLYlow,
        #     _PMLYhigh,
        #     _PMLZlow,
        #     _PMLZhigh,
        # )

        if time == None:
            time = self._total_time
        # validate x, y and z
        if x is not None:
            if not isinstance(x, int):
                raise ValueError("the `x`-location supplied should be a single integer")
            if y is not None or z is not None:
                raise ValueError(
                    "if an `x`-location is supplied, one should not supply a `y` or a `z`-location!"
                )
        elif y is not None:
            if not isinstance(y, int):
                raise ValueError("the `y`-location supplied should be a single integer")
            if z is not None or x is not None:
                raise ValueError(
                    "if a `y`-location is supplied, one should not supply a `z` or a `x`-location!"
                )
        elif z is not None:
            if not isinstance(z, int):
                raise ValueError("the `z`-location supplied should be a single integer")
            if x is not None or y is not None:
                raise ValueError(
                    "if a `z`-location is supplied, one should not supply a `x` or a `y`-location!"
                )
        else:
            raise ValueError(
                "at least one projection plane (x, y or z) should be supplied to visualize the grid!"
            )

        # Grid energy
        grid = self._grid
        grid_energy = bd.sum(grid.E ** 2 + grid.H ** 2, -1)
        if x is not None:
            assert grid.Ny > 1 and grid.Nz > 1
            xlabel, ylabel = "y", "z"
            Nx, Ny = grid.Ny, grid.Nz
            pbx, pby = "_PeriodicBoundaryY", "_PeriodicBoundaryZ"
            pmlxl, pmlxh, pmlyl, pmlyh = "_PMLYlow", "_PMLYhigh", "_PMLZlow", "_PMLZhigh"
            grid_energy = grid_energy[x, :, :].T
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.ylim(-1, Ny)
            # plt.xlim(-1, Nx)
        elif y is not None:
            assert grid.Nx > 1 and grid.Nz > 1
            xlabel, ylabel = "x", "z"
            Nx, Ny = grid.Nx, grid.Nz
            pbx, pby = "_PeriodicBoundaryX", "_PeriodicBoundaryZ"
            pmlxl, pmlxh, pmlyl, pmlyh = "_PMLXlow", "_PMLXhigh", "_PMLZlow", "_PMLZhigh"
            grid_energy = grid_energy[:, y, :].T
            # plt.gca().yaxis.set_ticks_position('right')
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.gca().yaxis.set_ticks_position('right')
            plt.ylim(-1, Ny)
            # plt.xlim(Nx, -1)
        elif z is not None:
            assert grid.Nx > 1 and grid.Ny > 1
            xlabel, ylabel = "x", "y"
            Nx, Ny = grid.Nx, grid.Ny
            pbx, pby = "_PeriodicBoundaryX", "_PeriodicBoundaryY"
            pmlxl, pmlxh, pmlyl, pmlyh = "_PMLXlow", "_PMLXhigh", "_PMLYlow", "_PMLYhigh"
            grid_energy = grid_energy[:, :, z].T
            # plt.gca().xaxis.set_ticks_position('top')
            # plt.gca().yaxis.set_ticks_position('right')
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.ylim(-1, Ny)
            # plt.ylim(Ny, -1)
            # plt.xlim(Nx, -1)
        else:
            raise ValueError("Visualization only works for 2D grids")

        for source in grid.sources:
            if isinstance(source, LineSource):
                if x is not None:
                    _x = [source.y[0], source.y[-1]]
                    _y = [source.z[0], source.z[-1]]
                elif y is not None:
                    _x = [source.x[0], source.x[-1]]
                    _y = [source.z[0], source.z[-1]]
                elif z is not None:
                    _x = [source.x[0], source.x[-1]]
                    _y = [source.y[0], source.y[-1]]
                plt.plot(_x, _y, lw=3, color=srccolor)
            elif isinstance(source, PointSource):
                if x is not None:
                    _x = source.y
                    _y = source.z
                elif y is not None:
                    _x = source.x
                    _y = source.z
                elif z is not None:
                    _x = source.x
                    _y = source.y
                plt.plot(_x - 0.5, _y - 0.5, lw=3, marker="o", color=srccolor)
                grid_energy[_x, _y] = 0  # do not visualize energy at location of source
            elif isinstance(source, PlaneSource):
                if x is not None:
                    _x = (
                        source.y
                        if source.y.stop > source.y.start + 1
                        else slice(source.y.start, source.y.start)
                    )
                    _y = (
                        source.z
                        if source.z.stop > source.z.start + 1
                        else slice(source.z.start, source.z.start)
                    )
                elif y is not None:
                    _x = (
                        source.x
                        if source.x.stop > source.x.start + 1
                        else slice(source.x.start, source.x.start)
                    )
                    _y = (
                        source.z
                        if source.z.stop > source.z.start + 1
                        else slice(source.z.start, source.z.start)
                    )
                elif z is not None:
                    _x = (
                        source.x
                        if source.x.stop > source.x.start + 1
                        else slice(source.x.start, source.x.start)
                    )
                    _y = (
                        source.y
                        if source.y.stop > source.y.start + 1
                        else slice(source.y.start, source.y.start)
                    )
                patch = ptc.Rectangle(
                    xy=(_x.start - 0.5, _y.start - 0.5),
                    width=_x.stop - _x.start,
                    height=_y.stop - _y.start,
                    linewidth=0,
                    edgecolor=srccolor,
                    facecolor=srccolor,
                )
                plt.gca().add_patch(patch)

        # Detector
        for detector in grid.detectors:
            if x is not None:
                _x = [detector.y[0], detector.y[-1]]
                _y = [detector.z[0], detector.z[-1]]
            elif y is not None:
                _x = [detector.x[0], detector.x[-1]]
                _y = [detector.z[0], detector.z[-1]]
            elif z is not None:
                _x = [detector.x[0], detector.x[-1]]
                _y = [detector.y[0], detector.y[-1]]

            if detector.__class__.__name__ == "BlockDetector":
                # BlockDetector
                plt.plot(
                    [_x[0], _x[1], _x[1], _x[0], _x[0]],
                    [_y[0], _y[0], _y[1], _y[1], _y[0]],
                    lw=3,
                    color=detcolor,
                )
            else:
                # LineDetector
                plt.plot(_x, _y, lw=3, color=detcolor)

        # Boundaries
        for boundary in grid.boundaries:
            if type(boundary).__name__ == pbx:
                _x = [-0.5, -0.5, float("nan"), Nx - 0.5, Nx - 0.5]
                _y = [-0.5, Ny - 0.5, float("nan"), -0.5, Ny - 0.5]
                plt.plot(_y, _x, color=pbcolor, linewidth=3)
            elif type(boundary).__name__ == pby:
                _x = [-0.5, Nx - 0.5, float("nan"), -0.5, Nx - 0.5]
                _y = [-0.5, -0.5, float("nan"), Ny - 0.5, Ny - 0.5]
                plt.plot(_y, _x, color=pbcolor, linewidth=3)
            elif type(boundary).__name__ == pmlyl:
                patch = ptc.Rectangle(
                    xy=(-0.5, -0.5),
                    width=Nx,
                    height=boundary.thickness,
                    linewidth=0,
                    edgecolor="none",
                    facecolor=pmlcolor,
                )
                plt.gca().add_patch(patch)
            elif type(boundary).__name__ == pmlxl:
                patch = ptc.Rectangle(
                    xy=(-0.5, -0.5),
                    width=boundary.thickness,
                    height=Ny,
                    linewidth=0,
                    edgecolor="none",
                    facecolor=pmlcolor,
                )
                plt.gca().add_patch(patch)
            elif type(boundary).__name__ == pmlyh:
                patch = ptc.Rectangle(
                    xy=(-0.5, Ny + 0.5 - boundary.thickness),
                    width=Nx,
                    height=boundary.thickness,
                    linewidth=0,
                    edgecolor="none",
                    facecolor=pmlcolor,
                )
                plt.gca().add_patch(patch)
            elif type(boundary).__name__ == pmlxh:
                patch = ptc.Rectangle(
                    xy=(Nx - boundary.thickness + 0.5, -0.5),
                    width=boundary.thickness,
                    height=Ny,
                    linewidth=0,
                    edgecolor="none",
                    facecolor=pmlcolor,
                )
                plt.gca().add_patch(patch)

        for obj in grid.objects:
            import numpy as np
            permittivity = np.sqrt(obj.permittivity)
            n = permittivity
            if x is not None and obj.x.start <= x <= obj.x.stop:
                _x = (obj.y.start, obj.y.stop)
                _y = (obj.z.start, obj.z.stop)
                n = permittivity[x - obj.x.start, :, :, :]
            elif y is not None and obj.y.start <= y <= obj.y.stop:
                _x = (obj.x.start, obj.x.stop)
                _y = (obj.z.start, obj.z.stop)
                n = permittivity[:, y - obj.y.start, :, :]
            elif z is not None and obj.z.start <= z <= obj.z.stop:
                _x = (obj.x.start, obj.x.stop)
                _y = (obj.y.start, obj.y.stop)
                n = permittivity[:, :, z - obj.z.start, :]
            else:
                continue
            px = min(_x)
            py = min(_y)
            for (mx, my), pmt in np.ndenumerate(n[:, :, 0]):
                if pmt != self.background_index:
                    rect = ptc.Rectangle((px + mx, py + my), 1, 1, facecolor=objcolor)
                    plt.gca().add_patch(rect)

            # patch = ptc.Rectangle(
            #     xy=(min(_y) - 0.5, min(_x) - 0.5),
            #     width=max(_y) - min(_y),
            #     height=max(_x) - min(_x),
            #     linewidth=0,
            #     edgecolor="none",
            #     facecolor=objcolor,
            # )
            # plt.gca().add_patch(patch)

        # visualize the energy in the grid
        cmap_norm = None
        if norm == "log":
            cmap_norm = LogNorm(vmin=1e-4, vmax=grid_energy.max() + 1e-4)
        if showEnergy:
            plt.imshow(abs(bd.numpy(grid_energy)), cmap=cmap, interpolation="sinc", norm=cmap_norm)

        # just to create the right legend entries:
        if legend:
            plt.plot([], lw=7, color=objcolor, label="Objects")
            plt.plot([], lw=7, color=pmlcolor, label="PML")
            plt.plot([], lw=3, color=pbcolor, label="Periodic Boundaries")
            plt.plot([], lw=3, color=srccolor, label="Sources")
            plt.plot([], lw=3, color=detcolor, label="Detectors")
            plt.figlegend()

        # finalize the plot
        plt.tight_layout()

        # save frame (require folder path and index)
        if save:
            if filePath is None:
                fileName = "file_"
                fileName += "x=" + str(x) + "," if x is not None else ""
                fileName += "y=" + str(y) + "," if y is not None else ""
                fileName += "z=" + str(z) + "," if z is not None else ""
                fileName += "show_energy=" + str(showEnergy) + ","
                fileName += "time=" + str(time) if time is not None else ""
                filePath = os.path.join(self.folder, f"{fileName}.png")
            plt.savefig(filePath)

        # show if not animating
        if show:
            plt.show()

        plt.clf()

    # def visualize_detector(self, name: str, axis: str = "x", field: str = "E", filepath: str = None, show=True,
    #                        save=False):
    #     """
    #
    #     Args:
    #
    #         name: Detector name.
    #         axis: Block detector data in axis {"x", "y", "z"}. default="x".
    #         field: field to show. {"E", "H"}. default="E".
    #         filepath: Figure path save to.
    #         show: If show the figure immediately. default=True
    #         show: If save the figure immediately. default=False
    #     """
    #     pass
    #     from tqdm import tqdm
    #     from scipy.signal import hilbert
    #     from numpy import log10, where
    #     from photfdtd.fdtd.detectors import LineDetector, BlockDetector
    #     target = None
    #     for detector in self._grid.detectors:
    #         if detector.name == name:
    #             target = detector
    #     if target is None:
    #         raise Exception(
    #             "No Detector named '{}' in grid.".format(name)
    #         )
    #     if save and filepath is None:
    #         filename = target.__class__.__name__ + "_" + field + axis
    #         filename += ",name="+name
    #         filename += ",time=" + str(self._total_time) if self._total_time is not None else ""
    #         filepath = os.path.join(self.folder, f"{filename}.png")
    #
    #     if isinstance(target, LineDetector):
    #         specific_plot = field + axis
    #         detector_dict = {}
    #         maxArray = {}
    #         detector_dict[name + " (E)"] = np.array([x for x in target.detector_values()["E"]])
    #         detector_dict[name + " (H)"] = np.array([x for x in target.detector_values()["H"]])
    #         if len(detector_dict):
    #             for detector in detector_dict:
    #                 if len(detector_dict[detector].shape) != 3:
    #                     print("Detector '{}' '{}' not LineDetector; dumped.".format(detector, specific_plot))
    #                     continue
    #                 if specific_plot is not None:
    #                     if detector[-2] != specific_plot[0]:
    #                         continue
    #                 if detector[-2] == "E":
    #                     plt.figure(0, figsize=(15, 15))
    #                 elif detector[-2] == "H":
    #                     plt.figure(1, figsize=(15, 15))
    #                 for dimension in range(len(detector_dict[detector][0][0])):
    #                     if specific_plot is not None:
    #                         if ["x", "y", "z"].index(specific_plot[1]) != dimension:
    #                             continue
    #                     # if specific_plot, subplot on 1x1, else subplot on 2x2
    #                     plt.subplot(
    #                         2 - int(specific_plot is not None),
    #                         2 - int(specific_plot is not None),
    #                         dimension + 1 if specific_plot is None else 1,
    #                     )
    #                     hilbertPlot = abs(
    #                         hilbert([x[0][dimension] for x in detector_dict[detector]])
    #                     )
    #                     plt.plot(hilbertPlot, label=detector)
    #                     plt.title(detector[-2] + "(" + ["x", "y", "z"][dimension] + ")")
    #                     if detector[-2] not in maxArray:
    #                         maxArray[detector[-2]] = {}
    #                     if str(dimension) not in maxArray[detector[-2]]:
    #                         maxArray[detector[-2]][str(dimension)] = []
    #                     maxArray[detector[-2]][str(dimension)].append(
    #                         [detector, where(hilbertPlot == max(hilbertPlot))[0][0]]
    #                     )
    #
    #                 # Loop same as above, only to add axes labels
    #                 for i in range(2):
    #                     if specific_plot is not None:
    #                         if ["E", "H"][i] != specific_plot[0]:
    #                             continue
    #                     plt.figure(i)
    #                     for dimension in range(len(detector_dict[detector][0][0])):
    #                         if specific_plot is not None:
    #                             if ["x", "y", "z"].index(specific_plot[1]) != dimension:
    #                                 continue
    #                         plt.subplot(
    #                             2 - int(specific_plot is not None),
    #                             2 - int(specific_plot is not None),
    #                             dimension + 1 if specific_plot is None else 1,
    #                         )
    #                         plt.xlabel("Time steps")
    #                         plt.ylabel("Magnitude")
    #                     plt.suptitle("Intensity profile")
    #             plt.legend()
    #             if save:
    #                 plt.savefig(filepath)
    #             if show:
    #                 plt.show()
    #             # plt.clf()  # 清除画布
    #     elif isinstance(target, BlockDetector):
    #         detector_data = np.array([x for x in target.detector_values()[field]])
    #         if len(detector_data) > 0:
    #             plt.ioff()
    #             plt.close()
    #             a = []  # array to store wave intensities
    #             axis_index = {"x": 0, "y": 1, "z": 2}
    #             for i in tqdm(range(len(detector_data[0]))):
    #                 a.append([])
    #                 for j in range(len(detector_data[0][0])):
    #                     temp = [x[i][j][0][axis_index[axis]] for x in detector_data]
    #                     a[i].append(max(temp) - min(temp))
    #
    #             peakVal, minVal = max(map(max, a)), min(map(min, a))
    #             print(
    #                 "Peak at:",
    #                 [
    #                     [[i, j] for j, y in enumerate(x) if y == peakVal]
    #                     for i, x in enumerate(a)
    #                     if peakVal in x
    #                 ],
    #             )
    #             a = 10 * log10([[y / minVal for y in x] for x in a])
    #
    #             plt.title("dB map of {} field distribution in detector region".format("Electrical(E)" if field == "E" else "Magnetic(H)"))
    #             plt.imshow(a, cmap="inferno", interpolation="spline16")
    #             cbar = plt.colorbar()
    #             cbar.ax.set_ylabel("dB scale", rotation=270)
    #             if save:
    #                 plt.savefig(filepath)
    #             if show:
    #                 plt.show()
    #             plt.clf()
    @staticmethod
    def dB_map(folder=None, total_time=None, block_det=None, data=None, choose_axis=2, field="E", name_det=None,
               interpolation="spline16", save=True, index="x-y"):
        """
        绘制场分贝图 需要面监视器数据
        @param folder: 保存图片的地址
        @param total_time: 模拟经历的时间
        @param block_det: 面监视器数据 此变量与data二选一即可
        @param data: reading_simulation()方法读取的data数据
        @param choose_axis: 从{0,1,2}中选择以匹配E或H的{x,y,z}分量
        @param field: “E”或“H”
        @param name_det: 监视器的名称
        @param interpolation: 绘图方式 'matplotlib.pyplot.imshow' interpolation
        @param save: bool 是否保存
        @param index: "x-y" or "y-z" or "x-z" 选择绘制dB图的面

        """
        if block_det != None:
            data = block_det
            name_det = block_det.name
        else:
            data = data[name_det + " (%s)" % field]
        fieldaxis = field + chr(choose_axis + 120)
        fdtd.dB_map_2D(block_det=data, choose_axis=choose_axis, interpolation=interpolation, index=index,
                       save=save, folder=folder, name_det=name_det, total_time=total_time, fieldaxis=fieldaxis)

    @staticmethod
    def plot_field(grid=None, field="E", axis=0, cross_section="z", axis_number=0, folder="", cmap="jet"):
        """
        绘制当前时刻场分布（不需要监视器）
        @param grid: grid
        @param field: "E"或"H"
        @param axis: 从{0,1,2}中选择以匹配E或H的{x,y,z}分量
        @param cross_section: "x"或"y"或"z"表示绘制哪个截面
        @param axis_number: 例如绘制z=0截面 ，则cross_section设为"z"而axis_number为0
        @param folder: 保存图片的地址
        @param cmap: matplotlib.pyplot.imshow(cmap)
        """
        title = "%s%s" % (field, chr(axis + 120))
        grid = grid._grid
        if field == "E":
            if cross_section == "z":
                field = grid.E[:, :, axis_number, axis]
            elif cross_section == "y":
                field = grid.E[:, axis_number, :, axis]
            elif cross_section == "x":
                field = grid.E[axis_number, :, :, axis]
        elif field == "H":
            if cross_section == "z":
                field = grid.H[:, :, axis_number, axis]
            elif cross_section == "y":
                field = grid.H[:, axis_number, :, axis]
            elif cross_section == "x":
                field = grid.H[axis_number, :, :, axis]

        m = max(abs(field.min().item()), abs(field.max().item()))

        # 创建颜色图
        plt.figure()
        plt.imshow(field, vmin=-m, vmax=m, cmap=cmap)  # cmap 可以选择不同的颜色映射

        # 添加颜色条
        cbar = plt.colorbar()
        # cbar.set_label('')

        # 添加标题和坐标轴标签
        plt.title(title)
        if cross_section == "z":
            plt.xlabel('X/grids')
            plt.ylabel('Y/grids')
        elif cross_section == "x":
            plt.xlabel('Y/grids')
            plt.ylabel('Z/grids')
        elif cross_section == "y":
            plt.xlabel('X/grids')
            plt.ylabel('Z/grids')

        plt.savefig(fname="%s//%s_%s=%i.png" % (folder, title, cross_section, axis_number))
        plt.close()

    @staticmethod
    def plot_fieldtime(folder=None, data=None, axis=2, field="E", index=0, index_3d=[0, 0, 0], name_det=None):
        """
        绘制监视器某一点的时域场图
        @param index_3d: 三维数组：用于面监视器，选择读取数据的点
        @param folder: 保存图片的文件夹
        @param data: read_simulation()读到的数据
        @param axis: 0或1或2分别表示E或H的x，y，z分量
        @param field: “E“或”H“
        @param index: 用于线监视器，选择读取数据的点
        @param name_det: 监视器的名称
        """
        data = data[name_det + " (%s)" % field]
        plt.figure()
        if data.ndim == 3:
            plt.plot(range(len(data)), data[:, index, axis], linestyle='-', label="Experiment")
            plt.ylabel('E%s' % chr(axis + 120))
            plt.xlabel("timesteps")
            plt.title("E%s-t" % chr(axis + 120))
            file_name = "E%s" % chr(axis + 120)
            plt.savefig(os.path.join(folder, f"{file_name}.png"))
            plt.close()
        else:
            plt.plot(range(len(data)), data[:, index_3d[0], index_3d[1], index_3d[2], axis], linestyle='-',
                     label="Experiment")
            plt.ylabel('E%s' % chr(axis + 120))
            plt.xlabel("timesteps")
            plt.title("E%s-t" % chr(axis + 120))
            file_name = "E%s" % chr(axis + 120)
            plt.savefig(os.path.join(folder, f"{file_name}.png"))
            plt.close()
