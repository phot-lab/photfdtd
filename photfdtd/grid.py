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


class Grid:

    def __init__(
            self, grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=20e-9, total_time=1, pml_width_x=10,
            pml_width_y=10, pml_width_z=0, permittivity=1.0, permeability=1.0, courant_number=None, foldername=" ", folder=None
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
            period: float = 15.0,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            name: str = None,
            pulse: bool = False,
            pulse_type: str = "gaussian",
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
        :param period: 周期
        :param amplitude: 振幅
        :param phase_shift: 相移
        :param name: 名称
        :param pulse: 脉冲（默认为否）
        :param cycle: 脉冲周期
        :param hanning_dt: 汉宁窗宽度（定义脉冲）
        :param polarization: 偏振
        :param pulse_length:脉宽 fs
        :param pulse_type: 脉冲类型 "gaussian" 或 "hanning" 或 "none"
        :param offset: 脉冲中心 fs
        :param x: 位置坐标（中心）
        :param y:
        :param z:
        :param xlength:
        :param ylength:
        :param zlength:
        :return:
        """
        # TODO：把线光源的更改运用到点光源和面光源
        x = x - xlength // 2
        y = y - ylength // 2
        z = z - zlength // 2
        if source_type == "pointsource":
            # 创建一个点光源
            x = x + xlength // 2
            y = y + ylength // 2
            z = z + zlength // 2

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
                self._grid[x: x + xlength, y: y + ylength] = fdtd.LineSource(
                    period=period,
                    amplitude=amplitude,
                    phase_shift=phase_shift,
                    name=name,
                    pulse=pulse,
                    pulse_type=pulse_type,
                    cycle=cycle,
                    pulse_length=pulse_length,
                    offset=offset
                )
            else:
                self._grid[x: x + xlength, y: y + ylength, z: z + zlength] = fdtd.LineSource(
                    period=period,
                    amplitude=amplitude,
                    phase_shift=phase_shift,
                    name=name,
                    pulse=pulse_type,
                    cycle=cycle,
                    pulse_length=pulse_length,
                    offset=offset
                )

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
        if axis == "x":  # 判断从哪一个轴俯视画图
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
        if animate == False:
            self._grid.run(total_time=self._total_time)
        elif animate:
            for i in range(self._total_time):
                self._grid.step()
                if (i+1) % step == 0:
                    self.save_fig(axis=axis, axis_number=axis_number, time=i)




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
        #TODO: fdtd原作者想要让这里的输入为监视器，但是他并没有完成这一代码，现在只能输入一维数据，完成它?
        #TODO: 傅里叶变换后的单位？
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