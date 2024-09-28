import photfdtd.fdtd as fdtd
import matplotlib.pyplot as plt
from .waveguide import Waveguide
import numpy as np
from numpy import savez
import os
from os import path, makedirs
from .analyse import Analyse
from .index import Index
import photfdtd.fdtd.constants as constants
import photfdtd.fdtd.conversions as conversions


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
            permittivity (float, optional): 环境相对介电常数 1.0
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

        if folder is not None:
            self.folder = folder
        else:
            current_dir = os.getcwd()
            self.folder = os.path.join(current_dir, foldername)
        makedirs(self.folder, exist_ok=True)

        self.background_index = np.sqrt(permittivity * permeability)
        self.flag_PML_not_set = True

    def _handle_unit(self, lengths, grid_spacing):
        # 把SI单位变成空间步长单位 SI unit -> grid spacing unit
        for i in range(len(lengths)):
            if not np.issubdtype(type(lengths[i]), np.integer) and lengths[i] is not None:
                # if not isinstance(lengths[i], int):
                lengths[i] = int(np.round(lengths[i] / grid_spacing))

        return lengths

    def _calculate_time(self):
        # calculate total time for FDTD simulation
        # return: total time in timesteps
        n = np.sqrt(1 / self._grid.inverse_permittivity.min())
        L = max(self._grid_xlength, self._grid_ylength, self._grid_zlength) * self._grid.grid_spacing
        time = int(L * 1.5 * n / constants.c / self._grid.time_step)  # Multiply 1.5 to make sure stabilization
        return time

    def _check_parameters(self, x_start=None, x_end=None, y_start=None, y_end=None, z_start=None, z_end=None,
                          object_to_check=None, name=None):
        # Check if the object exceeds the region
        if object_to_check:
            x_start, x_end, y_start, y_end, z_start, z_end = object_to_check.x, object_to_check.xlength + object_to_check.x, \
                object_to_check.y, object_to_check.ylength + object_to_check.y, \
                object_to_check.z, object_to_check.zlength + object_to_check.z
            name = object_to_check.name
        if max(x_start, x_end) > self._grid_xlength or min(x_start, x_end) < 0:
            raise ValueError("X range of %s (%i, %i) has exceeded the simulation region (0, %i)!"
                             % (name, x_start, x_end, self._grid_xlength))
        if max(y_start, y_end) > self._grid_ylength or min(y_start, y_end) < 0:
            raise ValueError("Y range of %s (%i, %i) has exceeded the simulation region (0, %i)!"
                             % (name, y_start, y_end, self._grid_ylength))
        if max(z_start, z_end) > self._grid_zlength or min(z_start, z_end) < 0:
            raise ValueError("Z range of %s (%i, %i) has exceeded the simulation region (0, %i)!"
                             % (name, z_start, z_end, self._grid_zlength))

    def add_object(self, object: Waveguide):

        for internal_object in object._internal_objects:

            if internal_object == 0:
                continue
            else:
                self._check_parameters(object_to_check=internal_object)
                self._grid[
                internal_object.x: internal_object.x + internal_object.xlength,
                internal_object.y: internal_object.y + internal_object.ylength,
                internal_object.z: internal_object.z + internal_object.zlength,
                ] = fdtd.Object(permittivity=internal_object.permittivity, name=internal_object.name,
                                background_index=internal_object.background_index,
                                priority_matrix=internal_object.priority_matrix)

    def del_object(self, object: Waveguide):
        for internal_object in object._internal_objects:

            if internal_object == 0:
                continue
            else:

                self._check_parameters(object_to_check=internal_object)
                self._grid[
                internal_object.x: internal_object.x + internal_object.xlength,
                internal_object.y: internal_object.y + internal_object.ylength,
                internal_object.z: internal_object.z + internal_object.zlength,
                ] = fdtd.Object(permittivity=self.background_index ** 2, name="deleted",
                                background_index=internal_object.background_index)
                self._grid.objects.pop(internal_object)
        pass

    def set_source(
            self,
            source_type: str = "pointsource",
            wavelength=None,
            period=None,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            name: str = "source",
            waveform: str = "gaussian",
            pulse_type: str = "none",
            cycle: int = 5,
            hanning_dt: float = 10.0,
            polarization: str = "x",
            pulse_length: float = 39e-15,
            offset: float = 50e-15,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            xlength: int or float = 0,
            ylength: int or float = 0,
            zlength: int or float = 0,
            x_start: int or float = None,
            y_start: int or float = None,
            z_start: int or float = None,
            x_end: int or float = None,
            y_end: int or float = None,
            z_end: int or float = None,
            axis: str = "y"
    ):
        """
        @param source_type: 光源种类：点或线或面 "pointsource", "linesource", "planesource"
        @param wavelength: 波长(m)
        @param period:周期
        @param amplitude: 振幅(V/m)
        @param phase_shift: 相移
        @param name: 名称
        @param waveform: default to "gaussian" 波形 "plane":平面波 "gaussian": 高斯波
        @param cycle: 汉宁窗脉冲的周期（仅使用汉宁hanning脉冲时有用）
        @param hanning_dt: 汉宁窗宽度（仅使用汉宁hanning脉冲时有用）
        @param polarization: 偏振
        @param pulse_type: 脉冲类型 "gaussian" 或 "hanning" 或 "CW"
        @param pulse_length: 脉宽(s)（仅用于高斯脉冲）
        @param offset: 脉冲中心(s)（仅用于高斯脉冲）
        @param x_start, y_start, z_start, x_end, y_end, z_end: parameters for 'linesource'
        @param x, y, z: center position, parameters for 'linesource' & pointsource
        @param xlength, ylength, zlength: cross length, parameters for '"planesource"
        @param axis: "x", "y", "z", only for "planesource"
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
        if pulse_type == "cw" or pulse_type == "CW" or pulse_type == "cW" or pulse_type == "Cw":
            pulse_type = "none"

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
            # if self._grid_ylength != 1:
            #     self._grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
            #     self._grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")
            if self._grid_zlength != 1:
                self._grid[:, :, 0:pml_width] = fdtd.PML(name="pml_zlow")
                self._grid[:, :, -pml_width:] = fdtd.PML(name="pml_zhigh")
            self.flag_PML_not_set = False
        xlength, ylength, zlength, x, y, z, x_start, y_start, z_start, x_end, y_end, z_end = self._handle_unit([xlength,
                                                                                                                ylength,
                                                                                                                zlength,
                                                                                                                x, y, z,
                                                                                                                x_start,
                                                                                                                y_start,
                                                                                                                z_start,
                                                                                                                x_end,
                                                                                                                y_end,
                                                                                                                z_end],
                                                                                                               grid_spacing=self._grid.grid_spacing)
        if x == None:
            # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
            x = int(self._grid_xlength / 2)
        if y == None:
            y = int(self._grid_ylength / 2)
        if z == None:
            z = int(self._grid_zlength / 2)

        if source_type == "pointsource":
            # 创建一个点光源
            # x = x + xlength // 2
            # y = y + ylength // 2
            # z = z + zlength // 2
            self._check_parameters(x, x, y, y, z, z)
            self._grid[x, y, z] = fdtd.PointSource(period=period, amplitude=amplitude, phase_shift=phase_shift,
                                                   name=name, cycle=cycle, hanning_dt=hanning_dt, pulse_type=pulse_type,
                                                   pulse_length=pulse_length, offset=offset, polarization=polarization)

        elif source_type == "linesource":  # 创建一个线光源

            if not x_start:
                x = x - xlength // 2
                x_start = x
                x_end = x + xlength
            if not y_start:
                y = y - ylength // 2
                y_start = y
                y_end = y + ylength
            if not z_start:
                z = z - zlength // 2
                z_start = z
                z_end = z + zlength

            self._check_parameters(x_start, x_end, y_start, y_end, z_start, z_end, name=name)
            if self._grid_zlength == 1:
                self._grid[x_start: x_end, y_start: y_end] = fdtd.LineSource(period=period, amplitude=amplitude,
                                                                             phase_shift=phase_shift, name=name,
                                                                             pulse_type=pulse_type, cycle=cycle,
                                                                             pulse_length=pulse_length,
                                                                             offset=offset,
                                                                             waveform=waveform,
                                                                             polarization=polarization)
            else:
                self._grid[x_start: x_end, y_start: y_end, z_start: z_end] = fdtd.LineSource(period=period,
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
            x = x - xlength // 2
            y = y - ylength // 2
            z = z - zlength // 2
            # 创建一个面光源

            if axis == "x":
                self._check_parameters(x, x, y, y + ylength, z, z + zlength, name=name)
                self._grid[x: x, y: y + ylength, z: z + zlength] = \
                    fdtd.PlaneSource(period=period, amplitude=amplitude, phase_shift=phase_shift, name=name,
                                     polarization=polarization)
            elif axis == "y":
                self._check_parameters(x, x + xlength, y, y, z, z + zlength, name=name)
                self._grid[x: x + xlength, y: y, z: z + zlength] = \
                    fdtd.PlaneSource(period=period, amplitude=amplitude, phase_shift=phase_shift, name=name,
                                     polarization=polarization)
            elif axis == "z":
                self._check_parameters(x, x + xlength, y, y + ylength, z, z, name=name)
                self._grid[x: x + xlength, y: y + ylength, z: z] = \
                    fdtd.PlaneSource(period=period, amplitude=amplitude, phase_shift=phase_shift, name=name,
                                     polarization=polarization)

        else:
            raise ValueError("Invalid source type.")

    def _try_to_find_source(self):
        try:
            found_source = self._grid.sources[0]
            print("Found source successfully without name")
            return found_source
        except:
            raise Exception("No source found in Grid.")

    def calculate_source_profile(self, time: int or float = None, source_name: str = None):
        if time is None:
            if self._grid.time_steps_passed != 0:
                time = self._grid.time_steps_passed
            else:
                time = 100e-15
        time = self._grid._handle_time(time)

        if source_name is not None:
            found_source = None
            for source in self._grid.sources:
                if source.name == source_name:
                    print("Found source successfully")
                    found_source = source
                    flag_found_source = True
                    break
            if found_source is None:
                print("There is no source named %s in the Grid, trying to find a source automatically." % source_name)
                found_source = self._try_to_find_source()
        else:
            found_source = self._try_to_find_source()
        x_sticks = np.linspace(0, len(found_source.profile), len(found_source.profile)) * self._grid.grid_spacing
        plt.plot(x_sticks, found_source.profile)
        plt.xticks()
        plt.xlabel('um')
        plt.ylabel("E")
        plt.title(f"{source_name}")
        plt.legend()
        file_name = "source_profile"
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))
        plt.close()

        if isinstance(found_source, fdtd.LineSource):
            print("This is a Linesource")
            size = len(found_source.profile)
            source_field = np.zeros((time, size, 3))
            _Epol = 'xyz'.index(found_source.polarization)
            for q in range(time):
                if found_source.pulse_type == "hanning":
                    t1 = int(2 * np.pi / (found_source.frequency * found_source.pulse_length / found_source.cycle))
                    if q < t1:
                        vect = found_source.profile * fdtd.waveforms.hanning(
                            found_source.frequency, q * found_source.pulse_length, found_source.cycle
                        )
                    else:
                        # src = - self.grid.E[self.x, self.y, self.z, 2]
                        vect = found_source.profile * 0
                elif found_source.pulse_type == "gaussian":
                    vect = found_source.profile * fdtd.waveforms.pulse_oscillation(frequency=found_source.frequency,
                                                                                   t=q * found_source.grid.time_step,
                                                                                   pulselength=found_source.pulse_length,
                                                                                   offset=found_source.offset)
                else:
                    vect = found_source.profile * np.sin(2 * np.pi * q / found_source.period + found_source.phase_shift)
                source_field[q, :, _Epol] = vect
        x_sticks = np.linspace(0, len(source_field), len(source_field)) * self._grid.time_step * 1e15
        plt.plot(x_sticks, source_field[:, int(size / 2), 0], label="Ex")
        plt.plot(x_sticks, source_field[:, int(size / 2), 1], label="Ey")
        plt.plot(x_sticks, source_field[:, int(size / 2), 2], label="Ez")
        plt.xticks()
        plt.xlabel('fs')
        plt.ylabel("amplitude")
        plt.title(f"Time Signal of {source_name}")
        plt.legend()
        file_name = "E_source"
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))
        plt.close()

        return source_field

    def set_detector(self,
                     detector_type: str = 'linedetector',
                     x_start: int or float = None,
                     y_start: int or float = None,
                     z_start: int or float = None,
                     x_end: int or float = None,
                     y_end: int or float = None,
                     z_end: int or float = None,
                     x: int or float = None,
                     y: int or float = None,
                     z: int or float = None,
                     xlength: int or float = 1,
                     ylength: int or float = 1,
                     zlength: int or float = 1,
                     name: str = 'detector',
                     axis: str = None,
                     ):
        """
        Adding detectors
        @param detector_type: 'blockdetector' or 'linedetector'
        @param x_start, y_start, z_start, x_end, y_end, z_end: parameters for 'linedetector'
        @param x, y, z: center position, parameters for 'blockdetector'
        @param xlength, ylength, zlength: cross length, parameters for 'blockdetector'
        @param name:
        @param axis: "x", "y", "z", only for blockdetector
        """

        if x == None:
            # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
            x = int(self._grid_xlength / 2)
        if y == None:
            y = int(self._grid_ylength / 2)
        if z == None:
            z = int(self._grid_zlength / 2)

        xlength, ylength, zlength, x, y, z, x_start, x_end, y_start, y_end, z_start, z_end = \
            self._handle_unit([xlength, ylength, zlength, x, y, z, x_start, x_end, y_start, y_end, z_start, z_end],
                              grid_spacing=self._grid.grid_spacing)

        # 设置监视器
        if detector_type == 'linedetector':

            if not x_start:
                x = x - xlength // 2
                x_start = x
                x_end = x + xlength
            if not y_start:
                y = y - ylength // 2
                y_start = y
                y_end = y + ylength
            if not z_start:
                z = z - zlength // 2
                z_start = z
                z_end = z + zlength

            self._check_parameters(x_start, x_end, y_start, y_end, z_start, z_end, name=name)
            self._grid[x_start: x_end, y_start: y_end, z_start: z_end] = fdtd.LineDetector(name=name)

        elif detector_type == 'blockdetector':

            if not axis:
                # Tell which dimension to draw automatically
                dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
                if not dims_with_size_one:
                    raise ValueError("Parameter 'axis' shouldn't be None for blockdetector in 3D simulation")
                axis = conversions.number_to_letter(dims_with_size_one[0])

            x -= int(xlength / 2)
            y -= int(ylength / 2)
            z -= int(zlength / 2)
            if axis == "x":
                self._check_parameters(x, x, y, y + ylength, z, z + zlength, name=name)
                self._grid[x: x,
                y: y + ylength,
                z: z + zlength] = fdtd.BlockDetector(name=name)
            elif axis == "y":
                self._check_parameters(x, x + xlength, y, y, z, z + zlength, name=name)
                self._grid[x: x + xlength,
                y: y,
                z: z + zlength] = fdtd.BlockDetector(name=name)
            elif axis == "z":
                self._check_parameters(x, x + xlength, y, y + ylength, z, z, name=name)
                self._grid[x: x + xlength,
                y: y + ylength,
                z: z] = fdtd.BlockDetector(name=name)
        else:
            raise ValueError("Invalid detector type.")

        def _try_to_find_detector(self):
            try:
                found_detector = self._grid.detectors[0]
                print("Found detector successfully without name")
                return found_detector
            except:
                raise Exception("No detector found in Grid.")

    def _try_to_find_detector(self):
        try:
            found_detector = self._grid.detectors[0]
            print("Found detector successfully without name")
            return found_detector
        except:
            raise Exception("No detector found in Grid.")

    def detector_profile(self, detector_name: str = None, field: str = "E", field_axis: str = "x", timesteps: int = -1):
        # TODO: block detector

        if detector_name is not None:
            found_detector = None
            for detector in self._grid.detectors:
                if detector.name == detector_name:
                    print("Found detector successfully")
                    found_detector = detector
                    flag_found_detector = True
                    break
            if found_detector is None:
                print(
                    "There is no detector named %s in the Grid, trying to find a detector automatically." % detector_name)
                found_detector = self._try_to_find_detector()
        else:
            found_detector = self._try_to_find_detector()
        # TODO:考虑y和z方向
        x = found_detector.x
        x = np.array(x) * self._grid.grid_spacing
        x_sticks = x
        field_number = conversions.letter_to_number(field_axis)
        detector_profile = np.array([x for x in found_detector.detector_values()["%s" % field]])[timesteps, :,
                           field_number]
        plt.plot(x_sticks, detector_profile)
        plt.xticks()
        plt.xlabel('um')
        plt.ylabel("E")
        plt.legend()
        plt.title(f"{detector_name}")
        file_name = "detector_profile_timestep=%i" % timesteps
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))
        plt.close()

    def save_fig(self,
                 axis=None,
                 axis_index=0,
                 axis_number=None,
                 animate=False,
                 time=None,
                 geo=None,
                 show_structure=True,
                 show_energy=False):
        """
        Saving the geometry figure. This function can also show energy while show_energy = True.
        @param geo: Optional: Solve.geometry, will be calculated automatically if None. 也可以为None，程序会自己计算
        @param axis: 轴(若为二维XY模拟，则axis只能='z')
        @param axis_index: index of axis
        @param axis_number: an outdated version of axis_index
        @param time: only for method run() 绘制哪个时刻的场图（用户用不到，仅供run()使用
        @param animate: 是否播放动画 #TODO: 这个参数的作用？
        :
        """
        # TODO: grid.visualize函数还有animate等功能，尚待加入
        if not axis:
            # Tell which dimension to draw automatically
            dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
            if not dims_with_size_one:
                raise ValueError("Parameter 'axis' should not be None for 3D simulation")
            axis = conversions.number_to_letter(dims_with_size_one[0])

        if axis_index is None:
            if axis_number is None:
                raise ValueError("Parameter 'axis_index' should not be None")
            else:
                axis_index = axis_number

        if not show_energy:
            time = 0

        else:
            time = self._grid.time_steps_passed
        index = "_%s=%d, total_time=%d" % (axis, axis_index, time)
        if self._grid is None:
            raise RuntimeError("The grid should have been set before saving figure.")

        axis = axis.lower()  # 识别大写的 "X"
        folder = self.folder
        if axis == "x":  # 绘制截面/剖面场图
            self._grid.visualize(x=axis_index, save=True, animate=animate,
                                 index=index, folder=folder, geo=geo,
                                 background_index=self.background_index, show_structure=show_structure,
                                 show_energy=show_energy)
        elif axis == "y":
            self._grid.visualize(y=axis_index, save=True, animate=animate,
                                 index=index, folder=folder, geo=geo,
                                 background_index=self.background_index, show_structure=show_structure,
                                 show_energy=show_energy)
        elif axis == "z":
            self._grid.visualize(z=axis_index, save=True, animate=animate,
                                 index=index, folder=folder, geo=geo,
                                 background_index=self.background_index, show_structure=show_structure,
                                 show_energy=show_energy)
        else:
            raise ValueError("Unknown axis parameter.")

        plt.close()  # 清除画布

    def plot_n(self,
               grid=None,
               axis: str = None,
               axis_index: int = 0,
               filepath: str = None):
        """
        Draw a refractive index plot. It is basically same with solve.plot().
        @param grid: Optional: photfdtd.grid
        @param axis:
        @param axis_index:
        @param filepath:
        """
        if not axis:
            # Tell which dimension to draw automatically
            dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
            if not dims_with_size_one:
                raise ValueError("Parameter 'axis' should not be None for 3D simulation")
            axis = conversions.number_to_letter(dims_with_size_one[0])
        if self:
            grid = self
        if not grid:
            raise ValueError("Parameter 'grid' shold not be None!")
        if not filepath:
            filepath = grid.folder
        grid = grid._grid
        geometry = np.sqrt(1 / np.float16(grid.inverse_permittivity))
        axis = axis.lower()

        # 去掉作为轴的那一维
        if axis == 'x':
            n = geometry[axis_index, :, :, :]
        elif axis == 'y':
            n = geometry[:, axis_index, :, :]
        elif axis == 'z':
            n = geometry[:, :, axis_index, :]
        else:
            raise ValueError('Parameter "axis" should be x, y or z! ')
        x = n.shape[0]
        y = n.shape[1]

        # It's quite important to transpose n
        from matplotlib import cm
        n = np.transpose(n, [1, 0, 2])
        plt.imshow(n[:, :, 0], cmap=cm.jet, origin="lower",
                   extent=[0, x * grid.grid_spacing * 1e6, 0, y * grid.grid_spacing * 1e6])
        plt.clim([np.amin(n), np.amax(n)])
        if axis == "x":
            plt.xlabel('y/um')
            plt.ylabel('z/um')
        elif axis == "y":
            plt.xlabel('x/um')
            plt.ylabel('z/um')
        elif axis == "z":
            plt.xlabel('x/um')
            plt.ylabel('y/um')
        plt.colorbar()
        plt.title("refractive_index_real")
        # 保存图片
        plt.savefig(fname='%s\\%s_%s=%d.png' % (filepath, 'index', axis, axis_index))

        # plt.show()
        plt.clf()
        plt.close()

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

        if not animate:
            if not isinstance(time, int):
                time = self._grid._handle_time(time)
            print("The total time for FDTD simulation is %i timesteps or %f fs." % (
                time, time * self._grid.time_step * 1e15))
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

    def calculate_Transmission(self, detector_name: str = None, field_axis: str = "x",
                               wl_start: float = 1400e-9, wl_end: float = 1700e-9,
                               detector_data: np.array = None, source_data: np.array = None,
                               detector_index: int = None,
                               source_name: str = None,
                               save_to_txt: bool = True,
                               grid=None) -> None:
        """
        # TODO:
        Calculate transmission spectrum, detector required.

        @param detector_name: The name of detector whose data will be calculated, can be None if there is only 1 detector in grid.
        @param source_name: The name of source whose data will be calculated, can be None if there is only 1 source in grid.
        @param field_axis: Optional: Default to "x"
        @param wl_start: Start wavelength
        @param wl_end: End wavelength
        @param detector_data: Optional: must be a 1 dimension array
        @param source_data: Optional: must be a 1 dimension array with same size as detector_data
        @param detector_index: Optional: Default to center of the detector
        @param save_to_txt: Optional: Default to True
        @param grid: Optinal: photfdtd.Grid instance
        """
        field_axis = fdtd.conversions.letter_to_number(field_axis)
        if grid is None:
            grid = self
        if detector_data is None:
            for detector in grid._grid.detectors:
                if detector.name == detector_name or detector_name is None:
                    detector_data = np.array([x for x in detector.detector_values()["E"]])
            if detector_index is None:
                detector_index = int(detector_data.shape[1] / 2)
            detector_data = detector_data[:, detector_index, field_axis]

        if source_data is None:
            source_data = grid.calculate_source_profile(time=grid._grid.time_steps_passed, source_name=source_name)
            source_data = source_data[:, int(source_data.shape[1] / 2), field_axis]

        detector_data = detector_data
        source_data = source_data

        fr_s = fdtd.FrequencyRoutines(grid._grid, objs=source_data)
        spectrum_freqs_s, spectrum_s = fr_s.FFT(
            freq_window_tuple=[constants.c / (wl_end), constants.c / (wl_start)], )

        fr_d = fdtd.FrequencyRoutines(grid._grid, objs=detector_data)
        spectrum_freqs_d, spectrum_d = fr_d.FFT(
            freq_window_tuple=[constants.c / (wl_end), constants.c / (wl_start)], )

        spectrum_wl = constants.c / (spectrum_freqs_s * (1e-6))
        Transmission = (abs(spectrum_d) / abs(spectrum_s)) ** 2
        Transmission[Transmission > 1] = 1
        plt.plot(spectrum_wl, Transmission)
        plt.xlabel('Wavelength (um)')
        plt.ylabel("T")
        plt.ylabel("Transmission")
        plt.savefig(os.path.join(grid.folder, f"{'Transmission_'}{detector_name}.png"))
        plt.close()

        if save_to_txt:
            np.savetxt('%s/Transmission.txt' % grid.folder, np.column_stack((spectrum_wl, Transmission)), fmt='%f',
                       delimiter='\t',
                       header='Wavelength (um)\tTransmission', comments='')

    def _sweep_(self,
                wl_start: float = 1.5,
                wl_end: float = 1.6,
                points: int = 100,
                material: str = "") -> None:
        """
        #TODO: 这个函数需要重写
        频率扫描
        @param material: 材料
        @param wl_start: 起始波长
        @param wl_end: 结束波长
        @param points: 计算点数
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

    def save_simulation(self):
        """ Save the Grid class instance into a ".npz" file"""
        import pickle
        # Serialize the class instance
        saved_grid = pickle.dumps(self)
        savez(path.join(self.folder, "detector_readings"), serialized_instance=saved_grid)
        # dic = {}
        # for detector in self._grid.detectors:
        #     dic[detector.name + " (E)"] = np.array([x for x in detector.detector_values()["E"]])
        #     dic[detector.name + " (H)"] = np.array([x for x in detector.detector_values()["H"]])
        # dic["grid_spacing"] = self._grid.grid_spacing
        # dic["time_step"] = self._grid.time_step
        # dic["detectors"] = self._grid.detectors
        # dic["sources"] = self._grid.sources
        # dic["time_passed"] = self._grid.time_passed
        # dic["grid"] = self
        #
        # # 保存detector_readings_sweep.npz文件
        # savez(path.join(self.folder, "detector_readings"), **dic)

    @staticmethod
    def read_simulation(folder: str = None):
        """读取保存的监视器数据
        静态方法，调用时应使用 data = Grid.read_simulation(folder="...")
        folder: 保存监视器数据的文件路径
        """
        if not folder:
            raise Exception("Please indicate the folder where your grid has been saved")
        import pickle
        if not folder.endswith(".npz"):
            folder = folder + "\detector_readings.npz"

        readings = np.load(folder, allow_pickle=True)

        return pickle.loads(readings['serialized_instance'])

    @staticmethod
    def dB_map(grid=None, folder=None, axis=None, field="E", field_axis="z",
               interpolation="spline16", total_time=None, save: bool = True):
        """
        Draw a field dB_map. At least 1 block detector is required. 绘制场分贝图 需要面监视器数据
        @param grid: Photfdtd.Grid
        @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
        @param axis: "x" or "y" or "z" 选择绘制dB图的截面
        @param field_axis: {x,y,z} of "E" or "H" field
        @param field: “E”或“H”
        @param interpolation: Optional. 'matplotlib.pyplot.imshow' interpolation 绘图方式
        @param save: bool, to save or not. 是否保存
        @param total_time: Optional, only used for title 模拟经历的时间，可选，仅命名用


        """
        if not axis:
            # Tell which dimension to draw automatically
            dims_with_size_one = [i for i, size in enumerate(grid._grid.inverse_permittivity.shape) if size == 1]
            if not dims_with_size_one:
                raise ValueError("Parameter 'axis' should not be None for 3D simulation")
            axis = conversions.number_to_letter(dims_with_size_one[0])
        if not folder:
            folder = grid.folder
        if not total_time:
            total_time = grid._grid.time_passed
        for detector in grid._grid.detectors:
            if isinstance(detector, fdtd.detectors.BlockDetector):
                fdtd.dB_map_2D(block_det=np.array([x for x in detector.detector_values()["%s" % field]]),
                               interpolation=interpolation, axis=axis, field=field, field_axis=field_axis,
                               save=save, folder=folder, name_det=detector.name, total_time=total_time)

            # dic[detector.name + " (E)"] = np.array([x for x in detector.detector_values()["E"]])
            # dic[detector.name + " (H)"] = np.array([x for x in detector.detector_values()["H"]])
        # if block_det != None:
        #     data = block_det
        #     name_det = block_det.name
        # else:
        #     data = data[name_det + " (%s)" % field]

    @staticmethod
    def plot_field(grid=None, axis=None, axis_index=0, field="E", field_axis=None, folder=None, cmap="jet",
                   show_geometry=True, show_field=True, vmax=None, vmin=None):
        """
        Plot a field map at current state. No need for detectors. 绘制当前时刻场分布（不需要监视器）
        @param show_geometry: bool 是否绘制波导结构
        @param show_field: bool 是否绘制场
        @param grid: Photfdtd.Grid
        @param field: "E"或"H"
        @param field_axis: {x,y,z,None} of E or H, if None, the energy intensity of E or H will be plotted
        @param axis: "x"或"y"或"z"表示绘制哪个截面
        @param axis_index: 例如绘制z=0截面 ，则axis设为"z"而axis_index为0
        @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
        @param cmap: Optional. matplotlib.pyplot.imshow(cmap)
        @param vmax: Optional. Max value of the color bar. 颜色条的最大、最小值
        @param vmin: Optional. Min value of the color bar.

        """

        if not show_field:
            title = "%s=%i" % (axis, axis_index)
        elif not field_axis:
            title = "%s intensity" % field
        else:
            title = "%s%s" % (field, field_axis)
        if not folder:
            folder = grid.folder
        background_index = grid.background_index
        grid = grid._grid
        if not show_field:
            if axis == "z":
                field = np.zeros_like(grid.E[:, :, axis_index, 0])
            elif axis == "y":
                field = np.zeros_like(grid.E[:, axis_index, :, 0])
            elif axis == "x":
                field = np.zeros_like(grid.E[axis_index, :, :, 0])
        else:
            if field == "E":
                if not field_axis:
                    # 能量
                    if axis == "z":
                        field = grid.E[:, :, axis_index, 0] ** 2 + grid.E[:, :, axis_index, 1] ** 2 + grid.E[:, :,
                                                                                                      axis_index,
                                                                                                      2] ** 2
                    elif axis == "y":
                        field = grid.E[:, axis_index, :, 0] ** 2 + grid.E[:, axis_index, :, 1] ** 2 + grid.E[:,
                                                                                                      axis_index,
                                                                                                      :, 2] ** 2
                    elif axis == "x":
                        field = grid.E[axis_index, :, :, 0] ** 2 + grid.E[axis_index, :, :, 1] ** 2 + grid.E[axis_index,
                                                                                                      :,
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
                                                                                                      axis_index,
                                                                                                      2] ** 2
                    elif axis == "y":
                        field = grid.H[:, axis_index, :, 0] ** 2 + grid.H[:, axis_index, :, 1] ** 2 + grid.H[:,
                                                                                                      axis_index,
                                                                                                      :, 2] ** 2
                    elif axis == "x":
                        field = grid.H[axis_index, :, :, 0] ** 2 + grid.H[axis_index, :, :, 1] ** 2 + grid.H[axis_index,
                                                                                                      :,
                                                                                                      :, 2] ** 2
                else:
                    if axis == "z":
                        field = grid.H[:, :, axis_index, ord(field_axis) - 120]
                    elif axis == "y":
                        field = grid.H[:, axis_index, :, ord(field_axis) - 120]
                    elif axis == "x":
                        field = grid.H[axis_index, :, :, ord(field_axis) - 120]
            if not vmax:
                # vmax = max(abs(field.min().item()), abs(field.max().item()))
                vmax = field.max().item()
            if not vmin:
                if not field_axis:
                    vmin = 0
                else:
                    vmin = field.min().item()

        # 创建颜色图
        plt.figure()

        plt.imshow(np.transpose(field), vmin=vmin, vmax=vmax, cmap=cmap,
                   extent=[0, field.shape[0] * grid.grid_spacing * 1e6, 0,
                           field.shape[1] * grid.grid_spacing * 1e6],
                   origin="lower")  # cmap 可以选择不同的颜色映射
        if show_field:
            cbar = plt.colorbar()
        if show_geometry:

            geo = np.sqrt(1 / np.float16(grid.inverse_permittivity))

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
        if show_field:
            fname = "%s//%s_%s=%i.png" % (folder, title, axis, axis_index)
        else:
            fname = "%s//%s.png" % (folder, title)
        plt.savefig(fname=fname)
        plt.close()

    @staticmethod
    def plot_fieldtime(grid=None, folder=None, field_axis="z", field="E", index=None, index_3d=None, name_det=None):
        """
        Draw and save the field vs time of a point. 绘制监视器某一点的时域场图
        @param grid: Photfdtd.Grid
        @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
        @param data: read_simulation()读到的数据
        @param field_axis: x, y, z of E or H
        @param field: “E“或”H“
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 三维数组：用于面监视器，选择读取数据的点
        @param name_det: 监视器的名称
        """
        data = None
        for detector in grid._grid.detectors:
            if detector.name == name_det:
                data = np.array([x for x in detector.detector_values()["%s" % field]])
        if data is None:
            print("ValueError when using plot_fieldtime: No detector named '%s'" % name_det)
            return
        if folder is None:
            folder = grid.folder
        plt.figure()

        if data.ndim == 3:
            if index == None:
                index = int(data.shape[1] / 2)
            plt.plot(range(len(data)), data[:, index, ord(field_axis) - 120], linestyle='-', label="Experiment")
            plt.ylabel('%s%s' % (field, field_axis))
            plt.xlabel("timesteps")
            plt.title("%s%s-t" % (field, field_axis))
            file_name = "%s%s" % (field, field_axis)
            plt.savefig(os.path.join(folder, f"{file_name}.png"))
            plt.close()
        else:
            if index_3d == None:
                index_3d = [int(data.shape[0] / 2), int(data.shape[1] / 2), int(data.shape[2] / 2)]
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
    def compute_frequency_domain(grid, wl_start, wl_end, name_det=None, input_data=None,
                                 index=0, index_3d=[0, 0, 0], field_axis="x", field="E", folder=None):
        """
        傅里叶变换绘制频谱
        @param grid: photfdtd.grid
        @param wl_start: 起始波长(m)
        @param wl_end: 结束波长(m)
        @param name_det: 监视器名称
        @param input_data: Optional: 如果输入了这个数据，则data、name_det、index、index_3d可以不输入。input_data必须是一个一维数组，
        其长度表示时间步长，每一个元素表示在该时间场的幅值。
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 用于面监视器，选择读取数据的点
        @param field_axis: "x", "y", "z"
        @param field: ”E"或"H"
        @param folder: Optional: default: grid.folder 保存图片的地址，若为None则为grid.folder
        """
        # TODO: axis参数与其他可视化参数一致
        # TODO: 把fdtd的fourier.py研究明白
        # TODO: 傅里叶变换后的单位？
        if field_axis is not None:
            field_axis = conversions.letter_to_number(field_axis)
        if folder is None:
            folder = grid.folder
        if input_data is None:
            for detector in grid._grid.detectors:
                if detector.name == name_det or name_det is None:
                    input_data = np.array([x for x in detector.detector_values()["%s" % field]])
                    name_det = detector.name
        if name_det is None:
            name_det = "Input_data"
        if input_data.ndim == 3:
            if not index:
                index = int(input_data.shape[1] / 2)
            input_data = input_data[:, index, field_axis]
        elif input_data.ndim == 5:
            if not index_3d:
                index_3d = [int(input_data.shape[0] / 2), int(input_data.shape[1] / 2), int(input_data.shape[2] / 2)]
            input_data = input_data[:, index_3d[0], index_3d[1], index_3d[2], field_axis]

        fr = fdtd.FrequencyRoutines(grid._grid, objs=input_data)
        spectrum_freqs, spectrum = fr.FFT(
            freq_window_tuple=[constants.c / (wl_end), constants.c / (wl_start)], )

        # 绘制频谱
        plt.plot(spectrum_freqs, spectrum)
        plt.xlabel('frequency (Hz)')
        plt.ylabel("spectrum")
        plt.title("Spectrum")
        file_name = "spectrum_%s%s_%s" % (field, chr(field_axis + 120), name_det)
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

        # 绘制频率-振幅
        plt.plot(spectrum_freqs, np.abs(spectrum))
        plt.xlabel('frequency (Hz)')
        plt.ylabel("amplitude")
        plt.title("Spectrum")
        file_name = "f-amplitude_%s%s_%s" % (field, chr(field_axis + 120), name_det)
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

        # 绘制波长-振幅
        plt.plot(constants.c / (spectrum_freqs * (1e-6)), np.abs(spectrum))
        plt.xlabel('wavelength (um)')
        plt.ylabel("amplitude")
        plt.title("Spectrum")
        file_name = "wl-amplitude_%s%s_%s" % (field, chr(field_axis + 120), name_det)
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

        return constants.c / (spectrum_freqs * (1e-6)), np.abs(spectrum)

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
                           grid_spacing=grid._grid.grid_spacing, foldername="%s_sliced_grid" % grid.folder,
                           permittivity=self.background_index ** 2)
        grid_sliced._grid.inverse_permittivity = grid._grid.inverse_permittivity[x_slice[0]:x_slice[1],
                                                 y_slice[0]:y_slice[1], z_slice[0]:z_slice[1]]

        return grid_sliced

    def visualize(self, axis=None, axis_index=None, field="E", field_axis=None):
        if not axis:
            # Tell which dimension to draw automatically
            dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
            if not dims_with_size_one:
                dims_with_size_one = [1]
                # raise ValueError("Parameter 'axis' should not be None for 3D simulation")
            axis = conversions.number_to_letter(dims_with_size_one[0])
        else:
            dims_with_size_one = [conversions.letter_to_number(axis)]
        if not axis_index:
            axis_index = int(self._grid.inverse_permittivity.shape[dims_with_size_one[0]] / 2)
        source = self._try_to_find_source()
        if field_axis == None:
            field_axis = source.polarization

        self.save_fig()
        self.plot_n()
        self.plot_field(grid=self, field=field, field_axis=field_axis, axis=axis, axis_index=axis_index, vmin=-1,
                        vmax=1)

        for detector in self._grid.detectors:
            self.detector_profile(detector_name=detector.name, field=field, field_axis=field_axis)
            self.plot_fieldtime(grid=self, field=field, field_axis=field_axis, name_det=detector.name)
            self.compute_frequency_domain(grid=self, wl_start=1400e-9, wl_end=1700e-9, name_det=detector.name,
                                          field=field, field_axis=field_axis)
            if isinstance(detector, fdtd.detectors.BlockDetector):
                self.dB_map(grid=self, field=field, field_axis=field_axis)
            self.calculate_Transmission(detector_name=detector.name, source_name=self._try_to_find_source())
        for source in self._grid.sources:
            self.calculate_source_profile(source_name=source.name)
