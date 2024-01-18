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
            self, grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=20e-9,
            # total_time=1,
            # pml_width_x=0,
            # pml_width_y=0, pml_width_z=0, 
            permittivity=1.0, permeability=1.0, courant_number=None, foldername=" ",
            folder=None
    ) -> None:
        """
        Args:
            grid_xlength (int or float, optional): xlength of Simulation Region, SI unit(m) if float or grid_spacing unit if int
            grid_ylength (int or float, optional): ylength of Simulation Region, SI unit(m) if float or grid_spacing unit if int
            grid_zlength (int or float, optional): zlength of Simulation Region, SI unit(m) if float or grid_spacing unit if int
            grid_spacing (float, optional): fdtd算法的空间步长（yee元胞的网格宽度）. 单位为m
            total_time (int, optional): 计算时间. Defaults to 1.
            pml_width (int, optional): PML宽度.
            permeability (float, optional): 环境相对磁导率 1.0
            permittivity (float, optional): 环境相对介电常数，二者共同决定了环境折射率 1.0
            (refractive_index ** 2 = permeability * permittivity, 对大部分材料permeability=1.0)
            courant_number: 科朗数 默认为None
            foldername: 文件夹名称, 若其不存在将在目录下创建该文件夹
        """

        grid_xlength, grid_ylength, grid_zlength = self._handle_unit(lengths=[grid_xlength, grid_ylength, grid_zlength],
                                                                     grid_spacing=grid_spacing)

        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength),
                         grid_spacing=grid_spacing,
                         permittivity=permittivity,
                         permeability=permeability,
                         courant_number=courant_number
                         )

        self._grid_xlength = grid_xlength
        self._grid_ylength = grid_ylength
        self._grid_zlength = grid_zlength
        # self._total_time = total_time
        self._grid = grid

        # makedirs(foldername, exist_ok=True)  # Output master folder declaration
        current_dir = os.getcwd()

        # self.folder: 保存结果的文件夹
        self.folder = os.path.join(current_dir, foldername)
        if folder != "" and folder is not None:
            self.folder = folder
        makedirs(self.folder, exist_ok=True)

        self.background_index = np.sqrt(permittivity * permeability)
        self.flag_PML_not_set = True

    def _handle_unit(self, lengths, grid_spacing):
        # 把SI单位变成空间步长单位 SI unit -> grid spacing unit
        for i in range(len(lengths)):
            if not np.issubdtype(type(lengths[i]), np.integer):
                # if not isinstance(lengths[i], int):
                lengths[i] = int(np.round(lengths[i] / grid_spacing))

        return lengths

    def _calculate_time(self):
        # calculate total time for FDTD simulation
        # return: total time in timesteps
        n = np.sqrt(1 / self._grid.inverse_permittivity.min())
        L = max(self._grid_xlength, self._grid_ylength, self._grid_zlength) * self._grid.grid_spacing
        time = int(L * n / constants.c / self._grid.time_step)
        return time

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
                ] = fdtd.Object(permittivity=internal_object.permittivity, name=internal_object.name,
                                background_index=internal_object.background_index)

    def set_source(
            self,
            source_type: str = "pointsource",
            wavelength=None,
            period=None,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            name: str = "source",
            waveform: str = "plane",
            pulse_type: str = "none",
            cycle: int = 5,
            hanning_dt: float = 10.0,
            polarization: str = "x",
            pulse_length: float = 39e-15,
            offset: float = 112e-15,
            x: int = 5,
            y: int = 5,
            z: int = 5,
            xlength: int or float = 5,
            ylength: int or float = 5,
            zlength: int or float = 5,
    ):
        """
        :param source_type: 光源种类：点或线或面
        :param wavelength: 波长(m)
        :param period:周期
        :param amplitude: 振幅(V/m)
        :param phase_shift: 相移
        :param name: 名称
        :param waveform: 波形 "plane":平面波 "gaussian": 高斯波
        :param cycle: 汉宁窗脉冲的周期（仅使用汉宁hanning脉冲时有用）
        :param hanning_dt: 汉宁窗宽度（仅使用汉宁hanning脉冲时有用）
        :param polarization: 偏振
        :param pulse_type: 脉冲类型 "gaussian" 或 "hanning" 或 "none"
        :param pulse_length: 脉宽(s)（仅用于高斯脉冲）
        :param offset: 脉冲中心(s)（仅用于高斯脉冲）
        :param x: 位置坐标（中心）
        :param y:
        :param z:
        :param xlength:
        :param ylength:
        :param zlength:
        """

        # if pml_width_x != 0:
        #     grid[0:pml_width_x, :, :] = fdtd.PML(name="pml_xlow")
        #     grid[-pml_width_x:, :, :] = fdtd.PML(name="pml_xhigh")
        # if pml_width_y != 0:
        #     grid[:, 0:pml_width_y, :] = fdtd.PML(name="pml_ylow")
        #     grid[:, -pml_width_y:, :] = fdtd.PML(name="pml_yhigh")
        # if pml_width_z != 0:
        #     grid[:, :, 0:pml_width_z] = fdtd.PML(name="pml_zlow")
        #     grid[:, :, -pml_width_z:] = fdtd.PML(name="pml_zhigh")

        if period is None:
            if wavelength is not None:
                period = wavelength / constants.c
            else:
                raise ValueError("please set wavelength or period for the source")

        if self.flag_PML_not_set:
            pml_width = self._handle_unit([(period * constants.c) / 2],
                                          grid_spacing=self._grid.grid_spacing)[0]
            if self._grid_xlength != 1:
                self._grid[0:pml_width, :, :] = fdtd.PML(name="pml_xlow")
                self._grid[-pml_width:, :, :] = fdtd.PML(name="pml_xhigh")
            if self._grid_ylength != 1:
                self._grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
                self._grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")
            if self._grid_zlength != 1:
                self._grid[:, :, 0:pml_width] = fdtd.PML(name="pml_zlow")
                self._grid[:, :, -pml_width:] = fdtd.PML(name="pml_zhigh")
            self.flag_PML_not_set = False
        xlength, ylength, zlength = self._handle_unit([xlength, ylength, zlength], grid_spacing=self._grid.grid_spacing)
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
                                                                             waveform=waveform,
                                                                             polarization=polarization)
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
            raise ValueError("Invalid source type.")

    def set_detector(self,
                     detector_type: str = 'linedetector',
                     x: int = 5,
                     y: int = 5,
                     z: int = 5,
                     xlength: int or float = 5,
                     ylength: int or float = 5,
                     zlength: int or float = 1,
                     name: str = 'detector'
                     ):

        xlength, ylength, zlength = self._handle_unit([xlength, ylength, zlength],
                                                      grid_spacing=self._grid.grid_spacing)
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
                 time=None,
                 geo=None,
                 show_structure=True,
                 show_energy=False):
        """
        Saving the geometry figure. This function can also show energy while show_energy = True.
        @param geo: Solve.geometry，也可以为None，程序会自己计算
        @param axis: 轴(若为二维XY模拟，则axis只能='z')
        @param axis_number: 索引
        @param time: 绘制哪个时刻的场图（用户用不到，仅供run()使用
        @param animate: 是否播放动画 #TODO: 这个参数的作用？
        :
        """
        # TODO: grid.visualize函数还有animate等功能，尚待加入
        if not show_energy:
            time = 0

        else:
            time = self._grid.time_steps_passed
        index = "_%s=%d, total_time=%d" % (axis, axis_number, time)
        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")

        axis = axis.lower()  # 识别大写的 "X"
        folder = self.folder
        if axis == "x":  # 绘制截面/剖面场图
            self._grid.visualize(x=axis_number, save=True, animate=animate,
                                 index=index, folder=folder, geo=geo,
                                 background_index=self.background_index, show_structure=show_structure,
                                 show_energy=show_energy)
        elif axis == "y":
            self._grid.visualize(y=axis_number, save=True, animate=animate,
                                 index=index, folder=folder, geo=geo,
                                 background_index=self.background_index, show_structure=show_structure,
                                 show_energy=show_energy)
        elif axis == "z":
            self._grid.visualize(z=axis_number, save=True, animate=animate,
                                 index=index, folder=folder, geo=geo,
                                 background_index=self.background_index, show_structure=show_structure,
                                 show_energy=show_energy)
        else:
            raise RuntimeError("Unknown axis parameter.")

        plt.close()  # 清除画布

    def run(self,
            animate: bool = False,
            step: int = 5,
            axis="x",
            axis_number=0,
            time=None
            ):
        """
        @param time: int for timesteps or float for seconds
        @param axis: 与save_fig()相同
        @param axis_number:
        @param animate: 是否播放动画 %TODO: 完成它
        @param step: 每多少个时间步绘一次图
        """
        axis = axis.lower()
        if time is None:
            time = self._calculate_time()
        if animate == False:
            if not isinstance(time, int):
                time = self._grid._handle_time(time)
            print("The total time for FDTD simulation in timesteps is %i" % time)
            self._grid.run(total_time=time)
        # elif animate:
        #     for i in range(self._total_time):
        #         self._grid.step()
        #         if (i + 1) % step == 0:
        #             if axis == "x":
        #                 self.visualize(x=axis_number, showEnergy=True, show=False, save=True, time=i)
        #             elif axis == "y":
        #                 self.visualize(y=axis_number, showEnergy=True, show=False, save=True, time=i)
        #             elif axis == "z":
        #                 self.visualize(z=axis_number, showEnergy=True, show=False, save=True, time=i)
        #             else:
        #                 continue

    def animate(self,
                axis: str = "z",
                number: int = 0):
        # TODO: 完成它，让正则表达式能识别完整地址
        pass
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
        # TODO: 保存和读取整个grid
        dic = {}
        for detector in self._grid.detectors:
            dic[detector.name + " (E)"] = np.array([x for x in detector.detector_values()["E"]])
            dic[detector.name + " (H)"] = np.array([x for x in detector.detector_values()["H"]])
        dic["grid_spacing"] = self._grid.grid_spacing
        dic["time_step"] = self._grid.time_step
        dic["detectors"] = self._grid.detectors
        dic["sources"] = self._grid.sources
        dic["time_passed"] = self._grid.time_passed

        # 保存detector_readings_sweep.npz文件
        savez(path.join(self.folder, "detector_readings"), **dic)

        return dic

    @staticmethod
    def read_simulation(folder: str = ''):
        """读取保存的监视器数据
        静态方法，调用时应使用 data = Grid.read_simulation(folder="...")
        folder: 保存监视器数据的文件路径
        """
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

    @staticmethod
    def dB_map(folder=None, total_time=None, block_det=None, data=None, axis="x", field="E", field_axis="z",
               name_det=None,
               interpolation="spline16", save=True, ):
        """
        绘制场分贝图 需要面监视器数据
        @param folder: 保存图片的地址
        @param total_time: 模拟经历的时间，可选，仅命名用
        @param block_det: 面监视器数据 此变量与data二选一即可
        @param data: reading_simulation()方法读取的data数据
        @param field_axis: {x,y,z} of E or H
        @param field: “E”或“H”
        @param name_det: 监视器的名称
        @param interpolation: 绘图方式 'matplotlib.pyplot.imshow' interpolation
        @param save: bool 是否保存
        @param axis: "x" or "y" or "z" 选择绘制dB图的截面

        """
        if block_det != None:
            data = block_det
            name_det = block_det.name
        else:
            data = data[name_det + " (%s)" % field]

        fdtd.dB_map_2D(block_det=data, interpolation=interpolation, axis=axis, field=field, field_axis=field_axis,
                       save=save,
                       folder=folder, name_det=name_det, total_time=total_time)

    @staticmethod
    def plot_field(grid=None, axis="z", axis_index=0, field="E", field_axis=None, folder="", cmap="jet",
                   show_geometry=True):
        """
        绘制当前时刻场分布（不需要监视器）
        @param show_geometry: bool 是否绘制波导结构
        @param grid: grid
        @param field: "E"或"H"
        @param field_axis: {x,y,z,None} of E or H, if None, the amplitude of E or H will be plotted
        @param axis: "x"或"y"或"z"表示绘制哪个截面
        @param axis_index: 例如绘制z=0截面 ，则axis设为"z"而axis_index为0
        @param folder: 保存图片的地址
        @param cmap: matplotlib.pyplot.imshow(cmap)
        """
        if not field_axis:
            title = "%s intensity" % field
        else:
            title = "%s%s" % (field, field_axis)
        background_index = grid.background_index
        grid = grid._grid
        if field == "E":
            if not field_axis:
                # 能量场
                if axis == "z":
                    field = grid.E[:, :, axis_index, 0] ** 2 + grid.E[:, :, axis_index, 1] ** 2 + grid.E[:, :,
                                                                                                  axis_index, 2] ** 2
                elif axis == "y":
                    field = grid.E[:, axis_index, :, 0] ** 2 + grid.E[:, axis_index, :, 1] ** 2 + grid.E[:, axis_index,
                                                                                                  :, 2] ** 2
                elif axis == "x":
                    field = grid.E[axis_index, :, :, 0] ** 2 + grid.E[axis_index, :, :, 1] ** 2 + grid.E[axis_index, :,
                                                                                                  :, 2] ** 2
            else:
                if axis == "z":
                    field = grid.E[:, :, axis_index, ord(field_axis) - 120]
                elif axis == "y":
                    field = grid.E[:, axis_index, :, ord(field_axis) - 120]
                elif axis == "x":
                    field = grid.E[axis_index, :, :, ord(field_axis) - 120]
        elif field == "H":
            if not field_axis:
                # 能量场
                if axis == "z":
                    field = grid.H[:, :, axis_index, 0] ** 2 + grid.H[:, :, axis_index, 1] ** 2 + grid.H[:, :,
                                                                                                  axis_index, 2] ** 2
                elif axis == "y":
                    field = grid.H[:, axis_index, :, 0] ** 2 + grid.H[:, axis_index, :, 1] ** 2 + grid.H[:, axis_index,
                                                                                                  :, 2] ** 2
                elif axis == "x":
                    field = grid.H[axis_index, :, :, 0] ** 2 + grid.H[axis_index, :, :, 1] ** 2 + grid.H[axis_index, :,
                                                                                                  :, 2] ** 2
            else:
                if axis == "z":
                    field = grid.H[:, :, axis_index, ord(field_axis) - 120]
                elif axis == "y":
                    field = grid.H[:, axis_index, :, ord(field_axis) - 120]
                elif axis == "x":
                    field = grid.H[axis_index, :, :, ord(field_axis) - 120]

        m = max(abs(field.min().item()), abs(field.max().item()))

        # 创建颜色图
        plt.figure()

        plt.imshow(np.transpose(field), vmin=-m, vmax=m, cmap=cmap,
                   extent=[0, field.shape[0] * grid.grid_spacing * 1e6, 0, field.shape[1] * grid.grid_spacing * 1e6],
                   origin="lower")  # cmap 可以选择不同的颜色映射
        cbar = plt.colorbar()
        if show_geometry:

            geo = np.sqrt(1 / grid.inverse_permittivity)

            # geo是四维矩阵
            geo = geo[:, :, :, -1]
            if axis == "x":
                n_to_draw = geo[axis_index, :, :]
            elif axis == "y":
                n_to_draw = geo[:, axis_index, :]
            elif axis == "z":
                n_to_draw = geo[:, :, axis_index]
            # n_to_draw /= n_to_draw.max()
            contour_data = np.where(n_to_draw != background_index, 1, 0)
            plt.contour(np.linspace(0, field.shape[0] * grid.grid_spacing * 1e6, field.shape[0]),
                        np.linspace(0, field.shape[1] * grid.grid_spacing * 1e6, field.shape[1]),
                        contour_data.T, colors='black', linewidths=1)

        # plt.ylim(-1, field.shape[1])
        # Make the figure full the canvas让画面铺满整个画布
        # plt.axis("tight")
        # 添加颜色条

        # cbar.set_label('')

        # 添加标题和坐标轴标签
        plt.title(title)

        if axis == "z":
            plt.xlabel('x/um')
            plt.ylabel('y/um')
        elif axis == "x":
            plt.xlabel('y/um')
            plt.ylabel('z/um')
        elif axis == "y":
            plt.xlabel('x/um')
            plt.ylabel('z/um')

        plt.savefig(fname="%s//%s_%s=%i.png" % (folder, title, axis, axis_index))
        plt.close()

    @staticmethod
    def plot_fieldtime(folder=None, data=None, field_axis="z", field="E", index=None, index_3d=None, name_det=None):
        """
        绘制监视器某一点的时域场图
        @param index_3d: 三维数组：用于面监视器，选择读取数据的点
        @param folder: 保存图片的文件夹
        @param data: read_simulation()读到的数据
        @param field_axis: x, y, z of E or H
        @param field: “E“或”H“
        @param index: 用于线监视器，选择读取数据的点
        @param name_det: 监视器的名称
        """
        data = data[name_det + " (%s)" % field]
        plt.figure()
        if data.ndim == 3:
            if index == None:
                raise ValueError("Parameter 'index' must be set for linedetector!")
            plt.plot(range(len(data)), data[:, index, ord(field_axis) - 120], linestyle='-', label="Experiment")
            plt.ylabel('%s%s' % (field, field_axis))
            plt.xlabel("timesteps")
            plt.title("%s%s-t" % (field, field_axis))
            file_name = "%s%s" % (field, field_axis)
            plt.savefig(os.path.join(folder, f"{file_name}.png"))
            plt.close()
        else:
            if index_3d == None:
                raise ValueError("Parameter 'index_3d' must be set for blockdetector!")
            plt.plot(range(len(data)), data[:, index_3d[0], index_3d[1], index_3d[2], ord(field_axis) - 120],
                     linestyle='-',
                     label="Experiment")
            plt.ylabel('%s%s' % (field, field_axis))
            plt.xlabel("timesteps")
            plt.title("%s%s-t" % (field, field_axis))
            file_name = "%s%s" % (field, field_axis)
            plt.savefig(os.path.join(folder, f"{file_name}.png"))
            plt.close()

    @staticmethod
    def compute_frequency_domain(grid, wl_start, wl_end, data, name_det, input_data=None,
                                 index=0, index_3d=[0, 0, 0], axis=0, field="E", folder=None):
        """
        傅里叶变换绘制频谱
        @param folder: 保存图片的地址，若为None则为grid.folder
        @param grid: photfdtd.grid
        @param wl_start: 起始波长(m)
        @param wl_end: 结束波长(m)
        @param data: save_simulation()方法保存的监视器数据
        @param name_det: 监视器名称
        @param input_data: 如果输入了这个数据，则data、name_det、index、index_3d可以不输入。input_data必须是一个一维数组，
        其长度表示时间步长，每一个元素表示在该时间场的幅值。
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 用于面监视器，选择读取数据的点
        @param axis: 0或1或2分别表示E或H的x，y，z分量
        @param field: ”E"或"H"
        """
        # TODO: 把fdtd的fourier.py研究明白
        # TODO: 傅里叶变换后的单位？
        if folder is None:
            folder = grid.folder
        if input_data is None:
            input_data = data[name_det + " (%s)" % field]
            del data
            if input_data.ndim == 3:
                input_data = input_data[:, index, axis]
            elif input_data.ndim == 5:
                input_data = input_data[:, index_3d[0], index_3d[1], index_3d[2], axis]

        fr = fdtd.FrequencyRoutines(grid._grid, objs=input_data)
        spectrum_freqs, spectrum = fr.FFT(
            freq_window_tuple=[constants.c / (wl_end), constants.c / (wl_start)], )

        # 绘制频谱
        plt.plot(spectrum_freqs, spectrum)
        plt.xlabel('frequency (Hz)')
        plt.ylabel("spectrum")
        file_name = "spectrum_%s%s" % (field, chr(axis + 120))
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

        # 绘制频率-振幅
        plt.plot(spectrum_freqs, np.abs(spectrum))
        plt.xlabel('frequency (Hz)')
        plt.ylabel("amplitude")
        file_name = "f-amplitude_%s%s" % (field, chr(axis + 120))
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

        # 绘制波长-振幅
        plt.plot(constants.c / (spectrum_freqs * (10e-6)), np.abs(spectrum))
        plt.xlabel('wavelength (um)')
        plt.ylabel("amplitude")
        file_name = "wl-amplitude_%s%s" % (field, chr(axis + 120))
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

    def slice_grid(self, grid=None, x_slice=[], y_slice=[], z_slice=[]):
        """切割grid，以切割后的grid创建grid_sliced
        @param grid: photfdtd.Grid
        @param x_slice: list. X range that will be sliced
        @param y_slice:
        @param z_slice:
        @return: Sliced grid
        """
        # TODO: 磁导率？
        if grid is None:
            grid = self

        grid_sliced = Grid(grid_xlength=x_slice[1] - x_slice[0], grid_ylength=y_slice[1] - y_slice[0],
                           grid_zlength=z_slice[1] - z_slice[0],
                           grid_spacing=grid._grid.grid_spacing, total_time=grid._total_time,
                           foldername="%s_sliced_grid" % grid.folder,
                           permittivity=self.background_index ** 2)
        grid_sliced._grid.inverse_permittivity = grid._grid.inverse_permittivity[x_slice[0]:x_slice[1],
                                                 y_slice[0]:y_slice[1], z_slice[0]:z_slice[1]]

        return grid_sliced
