import photfdtd
import photfdtd.fdtd as fdtd
import photfdtd.fdtd.backend as bd
import photfdtd.fdtd.constants as constants
import photfdtd.fdtd.conversions as conversions

import matplotlib.pyplot as plt
import numpy as np
import os
from dataclasses import dataclass
from typing import Optional
import h5py
import pickle


@dataclass
class Subregion:
    direction: str
    cell_size: float
    region_start: float
    region_end: float


class Grid:
    def __init__(
            self, grid_xlength=100, grid_ylength=200, grid_zlength=50,
            grid_spacing=20e-9,
            grid_spacing_x: float = None,
            grid_spacing_y: float = None,
            grid_spacing_z: float = None,
            subregions: list = None,
            permittivity=1.0, permeability=1.0,
            courant_number=None,
            foldername=" ",
            folder=None,
            set_PML: bool = True
    ) -> None:
        """
        Args:
            grid_xlength (int or float): xlength of Simulation Region, SI unit(m) if float or grid_spacing unit if int
            grid_ylength (int or float): ylength of Simulation Region, SI unit(m) if float or grid_spacing unit if int
            grid_zlength (int or float): zlength of Simulation Region, SI unit(m) if float or grid_spacing unit if int
            grid_spacing_x (float, optional): grid spacing in x direction, SI unit(m)
            grid_spacing_y (float, optional): grid spacing in y direction, SI unit(m)
            grid_spacing_z (float, optional): grid spacing in z direction, SI unit(m)
            grid_spacing (float): grid spacing in general, SI unit(m)
            permeability (float, optional): magnetic relative permeability of the background,环境相对磁导率 1.0
            permittivity (float, optional): electrical relative permittivity of the background,环境相对介电常数 1.0
            (refractive_index ** 2 = permeability * permittivity, 对大部分材料permeability=1.0)
            courant_number: 科朗数，None为默认
            foldername: 保存结果的文件夹名称
            folder: 保存结果的文件夹路径, None为当前目录下的foldername
            set_PML: 是否设置PML边界条件, 默认True
        Note:
            The units of E and H field in this package have been scaled:
            E(r, t) = √ϵ0 x E_real(r, t)
            H(r, t) = √μ0 x H_real(r, t)
        Example:
            grid = Grid(grid_xlength=4e-6, grid_ylength=4e-6, grid_zlength=4e-6, grid_spacing=20e-9,
            permittivity=background_index ** 2, foldername="test_torch")
        """
        if grid_spacing_x is None:
            grid_spacing_x = grid_spacing
        if grid_spacing_y is None:
            grid_spacing_y = grid_spacing
        if grid_spacing_z is None:
            grid_spacing_z = grid_spacing
        grid_xlength = self._handle_unit(lengths=[grid_xlength],
                                         grid_spacing=grid_spacing_x)[0]
        grid_ylength = self._handle_unit(lengths=[grid_ylength],
                                         grid_spacing=grid_spacing_y)[0]
        grid_zlength = self._handle_unit(lengths=[grid_zlength],
                                         grid_spacing=grid_spacing_z)[0]
        if folder is not None:
            self.folder = folder
        else:
            current_dir = os.getcwd()
            self.folder = os.path.join(current_dir, foldername)
        os.makedirs(self.folder, exist_ok=True)

        self.x_coordinates = bd.full(grid_xlength, grid_spacing_x)
        self.y_coordinates = bd.full(grid_ylength, grid_spacing_y)
        self.z_coordinates = bd.full(grid_zlength, grid_spacing_z)

        if subregions is not None:
            grid_xlength, grid_ylength, grid_zlength = self.add_subregion(subregions=subregions,
                                                                          grid_spacing_x=grid_spacing_x,
                                                                          grid_spacing_y=grid_spacing_y,
                                                                          grid_spacing_z=grid_spacing_z)
        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength),
                         grid_spacing=grid_spacing,
                         grid_spacing_x=grid_spacing_x,
                         grid_spacing_y=grid_spacing_y,
                         grid_spacing_z=grid_spacing_z,
                         permittivity=permittivity,
                         permeability=permeability,
                         courant_number=courant_number,
                         folder=self.folder
                         )

        self._grid_xlength = grid_xlength
        self._grid_ylength = grid_ylength
        self._grid_zlength = grid_zlength
        # self._total_time = total_time
        self._grid = grid

        self.background_index = bd.sqrt(bd.array(permittivity) * bd.array(permeability))

        self.flag_PML_not_set = True if set_PML else False

    def _handle_unit(self, lengths, grid_spacing=None) -> list:
        """处理单位，将SI单位转换为网格间距单位
        Handle the unit of lengths, convert SI units to grid spacing units.
        Args:
            lengths (list): 长度列表，SI单位(m)
            grid_spacing (float, optional): 网格间距单位，默认为None，使用Grid对象的grid_spacing属性
        Returns:
            list: 转换后的长度列表，单位为网格间距单位
        Examples:
            xlength, x, = grid._handle_unit([xlength, x], grid_spacing=grid._grid.grid_spacing_x)
            xlength = grid._handle_unit([xlength], grid_spacing=grid._grid.grid_spacing_x)[0]
            """
        if grid_spacing is None:
            grid_spacing = self._grid.grid_spacing
        # 把SI单位变成空间步长单位 SI unit -> grid spacing unit
        for i in range(len(lengths)):
            if not isinstance(lengths[i], int) and lengths[i] is not None:
                # if not isinstance(lengths[i], int):
                lengths[i] = int(bd.round(lengths[i] / grid_spacing))

        return lengths

    def _calculate_time(self) -> int:
        """calculate total time for FDTD simulation
        return: total time in timesteps"""
        n = bd.sqrt(1 / self._grid.inverse_permittivity.min())
        # 默认传播方向为z default propagating direction: z
        L = max(self._grid_xlength, self._grid_ylength, self._grid_zlength) * self._grid.grid_spacing_z
        time = int(L * 1.5 * n / constants.c / self._grid.time_step)  # Multiply 1.5 to make sure stabilization
        return time

    def _check_parameters(self,
                          x_start=None, x_end=None, y_start=None, y_end=None, z_start=None, z_end=None,
                          object_to_check=None, name=None) -> None:
        """检查参数是否在网格范围内
        Check if the parameters are within the grid range.
            """
        if object_to_check:
            obj = object_to_check  # 缓存引用
            x_start, x_end = obj.x, obj.xlength + obj.x
            y_start, y_end = obj.y, obj.ylength + obj.y
            z_start, z_end = obj.z, obj.zlength + obj.z
            name = obj.name

        # 缓存网格长度
        grid_x, grid_y, grid_z = self._grid_xlength, self._grid_ylength, self._grid_zlength

        if max(x_start, x_end) > grid_x or min(x_start, x_end) < 0:
            raise ValueError("X range of %s (%i, %i) has exceeded the simulation region (0, %i)!"
                             % (name, x_start, x_end, grid_x))
        if max(y_start, y_end) > grid_y or min(y_start, y_end) < 0:
            raise ValueError("Y range of %s (%i, %i) has exceeded the simulation region (0, %i)!"
                             % (name, y_start, y_end, grid_x))
        if max(z_start, z_end) > grid_z or min(z_start, z_end) < 0:
            raise ValueError("Z range of %s (%i, %i) has exceeded the simulation region (0, %i)!"
                             % (name, z_start, z_end, grid_z))

    def add_subregion(self,
                      subregions: list = None,
                      direction='x',
                      grid_spacing_x=None,
                      grid_spacing_y=None,
                      grid_spacing_z=None):
        """王硕在做"""
        return
        # subregions中每个方向仅允许有一个subregion
        for subregion in subregions:
            cell_size = subregion.cell_size
            region_start = subregion.region_start
            region_end = subregion.region_end
            if direction == "x":
                self.start_coordinates = round(region_start / grid_spacing_x)
                self.end_coordinates = round(region_end / grid_spacing_x)
                subregion_x_coordinates = bd.full(int((region_end - region_start) / cell_size), cell_size)
                self.x_coordinates = bd.concatenate([self.x_coordinates[:self.start_coordinates],
                                                     subregion_x_coordinates,
                                                     self.x_coordinates[end_coordinates:]])
            if direction == "y":
                start_coordinates = round(region_start / grid_spacing_y)
                end_coordinates = round(region_end / grid_spacing_y)
                subregion_y_coordinates = bd.full(int((region_end - region_start) / cell_size), cell_size)
                self.y_coordinates = bd.concatenate([self.y_coordinates[:start_coordinates],
                                                     subregion_y_coordinates,
                                                     self.y_coordinates[end_coordinates:]])
            if direction == "z":
                start_coordinates = round(region_start / grid_spacing_z)
                end_coordinates = round(region_end / grid_spacing_z)
                subregion_z_coordinates = bd.full(int((region_end - region_start) / cell_size), cell_size)
                self.z_coordinates = bd.concatenate([self.z_coordinates[:start_coordinates],
                                                     subregion_z_coordinates,
                                                     self.z_coordinates[end_coordinates:]])
        self.subregion_added = True
        return len(self.x_coordinates), len(self.y_coordinates), len(self.z_coordinates)

    # def handle_subregion(self, array, subregions: list = None):
    #     import scipy.ndimage
    #     def _zoom(array, axis, start, end, new_len):
    #
    #         zoom_factor = new_len / (end - start)  # 2 倍缩放
    #         if axis == 0:
    #             zoom = (zoom_factor, 1, 1)
    #         elif axis == 1:
    #             zoom = (1, zoom_factor, 1)
    #         elif axis == 2:
    #             zoom = (1, 1, zoom_factor)
    #         # 对选中的部分进行缩放
    #         zoomed_part = scipy.ndimage.zoom(array[:, start:end, :], zoom, order=0)
    #         return bd.concatenate([array[:, :start, :], zoomed_part, array[:, end:, :]], axis=1)
    #     _zoom(array, axis=0, start=0, end=10, new_len=20)
    #     _zoom(array, axis=1, start=0, end=10, new_len=20)
    #     _zoom(array, axis=2, start=0, end=10, new_len=20)
    #
    #     pass

    def add_object(self, object: photfdtd.Waveguide):
        """添加一个光学波导到网格中
        Add an optical waveguide to the grid.
        Args:
            object: photfdtd.Waveguide object, the waveguide to be added to the grid
            """
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

    def del_object(self, object: photfdtd.Waveguide):
        # TODO: unfinished, no use
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
                                background_index=internal_object.background_index,
                                priority_matrix=internal_object.priority_matrix)
                self._grid.objects.pop(internal_object)
        return

    def set_PML(self,
                pml_width=None,
                pml_width_x=None,
                pml_width_y=None,
                pml_width_z=None) -> None:
        """
        设置PML边界条件
        :param pml_width:
        :param pml_width_x:
        :param pml_width_y:
        :param pml_width_z:
        :return: None
        """
        if pml_width is not None:
            pml_width_x = pml_width if pml_width_x is None else pml_width_x
            pml_width_y = pml_width if pml_width_y is None else pml_width_y
            pml_width_z = pml_width if pml_width_z is None else pml_width_z
        pml_width_x = self._handle_unit([pml_width_x],
                                        grid_spacing=self._grid.grid_spacing_x)[0]
        pml_width_y = self._handle_unit([pml_width_y],
                                        grid_spacing=self._grid.grid_spacing_y)[0]
        pml_width_z = self._handle_unit([pml_width_z],
                                        grid_spacing=self._grid.grid_spacing_z)[0]
        if self._grid_xlength != 1 and pml_width_x is not None and pml_width_x > 0:
            self._grid[0:pml_width_x, :, :] = fdtd.PML(name="pml_xlow")
            self._grid[-pml_width_x:, :, :] = fdtd.PML(name="pml_xhigh")
        if self._grid_ylength != 1 and pml_width_y is not None and pml_width_y > 0:
            self._grid[:, 0:pml_width_y, :] = fdtd.PML(name="pml_ylow")
            self._grid[:, -pml_width_y:, :] = fdtd.PML(name="pml_yhigh")
        if self._grid_zlength != 1 and pml_width_z is not None and pml_width_z > 0:
            self._grid[:, :, 0:pml_width_z] = fdtd.PML(name="pml_zlow")
            self._grid[:, :, -pml_width_z:] = fdtd.PML(name="pml_zhigh")
        self.flag_PML_not_set = False

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
        Set a source in the grid.
        Args:
            @param source_type: 光源种类：点或线或面 "pointsource", "linesource", "planesource"
            @param wavelength: 波长(m)
            @param period:周期
            @param amplitude: 振幅
            @param phase_shift: 相移
            @param name: 名称
            @param waveform: default to "gaussian" 波形 "plane":平面波 "gaussian": 高斯波
            @param cycle: number of cycles of Hanning window pulse汉宁窗脉冲的周期数（仅使用汉宁hanning脉冲时有用）
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

        if pulse_type == "cw" or pulse_type == "CW" or pulse_type == "cW" or pulse_type == "Cw":
            # 如果是连续波光源 If it is a continuous wave source
            pulse_type = "none"

        if period is None:
            if wavelength is not None:
                period = wavelength / constants.c
            else:
                raise ValueError("please set wavelength or period for the source")

        ###
        if self.flag_PML_not_set:
            self.set_PML((period * constants.c) / 2)

        xlength, x, x_start, x_end = self._handle_unit([xlength, x, x_start, x_end],
                                                       grid_spacing=self._grid.grid_spacing_x)
        ylength, y, y_start, y_end = self._handle_unit([ylength, y, y_start, y_end],
                                                       grid_spacing=self._grid.grid_spacing_y)
        zlength, z, z_start, z_end = self._handle_unit([zlength, z, z_start, z_end],
                                                       grid_spacing=self._grid.grid_spacing_z)
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
                                     waveform=waveform, polarization=polarization, pulse_type=pulse_type,
                                     pulse_length=pulse_length, offset=offset, axis=axis)
            elif axis == "y":
                self._check_parameters(x, x + xlength, y, y, z, z + zlength, name=name)
                self._grid[x: x + xlength, y: y, z: z + zlength] = \
                    fdtd.PlaneSource(period=period, amplitude=amplitude, phase_shift=phase_shift, name=name,
                                     waveform=waveform, polarization=polarization, pulse_type=pulse_type,
                                     pulse_length=pulse_length, offset=offset, axis=axis)
            elif axis == "z":
                self._check_parameters(x, x + xlength, y, y + ylength, z, z, name=name)
                self._grid[x: x + xlength, y: y + ylength, z: z] = \
                    fdtd.PlaneSource(period=period, amplitude=amplitude, phase_shift=phase_shift, name=name,
                                     waveform=waveform, polarization=polarization, pulse_type=pulse_type,
                                     pulse_length=pulse_length, offset=offset, axis=axis)

        else:
            raise ValueError("Invalid source type.")

    def _try_to_find_source(self):
        """尝试在网格中找到一个光源
        Try to find a source in the grid.
        Returns:
            fdtd.Source: the first source found in the grid
        """
        try:
            found_source = self._grid.sources[0]
            print(f"Found source successfully: {found_source.name}")
            return found_source
        except:
            raise Exception("No source found in Grid.")

    def source_data(self,
                    time: Optional[int] or Optional[float] = None,
                    source_name: Optional[str] = None):
        """
        获取光源数据，绘制光源的空间分布、时域信号和频谱
        Get the source data from the grid.
        :param time: if None, use the current time steps passed in the grid. Or in timesteps(int) or in second(float).
        :param source_name: If None, try to find a source automatically. If specified, find the source with the name.
        :return: found_source, source_field, spectrum
        """
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
            source_name = found_source.name
        # TODO: y和z分量

        if isinstance(found_source, fdtd.LineSource):
            print("This is a Linesource")
            source_profile = found_source.profile
            size = len(found_source.profile)
            source_field = bd.zeros((time, size, 3))
        elif isinstance(found_source, fdtd.PointSource):
            print("This is a Pointsource")
            source_profile = found_source.sim_amplitude
            size = 1
            source_field = bd.zeros((time, size, 3))
        elif isinstance(found_source, fdtd.PlaneSource):
            print("This is a Planesource")
            # TODO: To be finished
            source_profile = found_source.profile
            shape = found_source.profile.shape
            source_field = bd.zeros((time, shape[0], shape[1], shape[2], 3))

        _Epol = 'xyz'.index(found_source.polarization)
        for q in range(time):
            if found_source.pulse_type == "hanning":
                t1 = int(2 * bd.pi / (found_source.frequency * found_source.pulse_length / found_source.cycle))
                if q < t1:
                    vect = source_profile * fdtd.waveforms.hanning(
                        found_source.frequency, q * found_source.pulse_length, found_source.cycle
                    )
                else:
                    # src = - self.grid.E[self.x, self.y, self.z, 2]
                    vect = source_profile * 0
            elif found_source.pulse_type == "gaussian":
                vect = source_profile * fdtd.waveforms.pulse_oscillation(frequency=found_source.frequency,
                                                                         t=q * found_source.grid.time_step,
                                                                         pulselength=found_source.pulse_length,
                                                                         offset=found_source.offset)
            else:
                vect = source_profile * bd.sin(2 * bd.pi * q / found_source.period + found_source.phase_shift)

            if isinstance(found_source, fdtd.PlaneSource):
                source_field[q, :, :, :, _Epol] = bd.array(vect)
            else:
                source_field[q, :, _Epol] = bd.array(vect)

        # convert to world E
        source_field = conversions.simE_to_worldE(source_field)
        # Spectrum
        if isinstance(found_source, fdtd.PlaneSource):
            fr = fdtd.FrequencyRoutines(self._grid, objs=source_field[:, int(shape[0] / 2), int(shape[1] / 2),
                                                         int(shape[2] / 2), _Epol])
        else:
            fr = fdtd.FrequencyRoutines(self._grid, objs=source_field[:, int(size / 2), _Epol])
        # TODO: 为什么是2*bandwidth
        spectrum_freqs, fourier = fr.FFT(
            freq_window_tuple=[found_source.frequency - 2 * found_source.bandwidth,
                               found_source.frequency + 2 * found_source.bandwidth], )

        spectrum = abs(fourier)
        # time
        time = bd.linspace(0, len(source_field), len(source_field)) * self._grid.time_step * 1e15

        # 创建一个画布，包含两个子图
        fig, axes = plt.subplots(2, 2, figsize=(12, 6))  # 1行2列的子图

        # 左侧子图: 源 Profile (space distribution)图
        if isinstance(found_source, fdtd.PointSource):
            axes[0][0].clear()  # 清空当前子图
            axes[0][0].axis("off")  # 关闭坐标轴
            axes[0][0].text(0.5, 0.5, "Space distribution is unavailable for point source",
                            ha="center", va="center", fontsize=12)  # 居中显示文本
        elif isinstance(found_source, fdtd.LineSource):
            length = bd.linspace(0, len(found_source.profile), len(found_source.profile)) * self._grid.grid_spacing_x
            axes[0][0].plot(bd.numpy(length * 1e6),
                            bd.numpy(conversions.simE_to_worldE(found_source.profile)))
            # axes[0][0].set_xticks()  # 每隔10个显示一个刻度
            axes[0][0].set_xlabel('um')
            axes[0][0].set_ylabel(f"E{conversions.number_to_letter(_Epol)} (V/m)")
            axes[0][0].set_title(f"Space distribution")
            axes[0][0].legend(["Source Profile"])
        elif isinstance(found_source, fdtd.PlaneSource):
            # 选择方向
            shape = source_profile.shape

            # 找到 shape 中值为 1 的维度
            squeeze_axis = bd.where(bd.array(shape) == 1)[0]

            if len(squeeze_axis) == 1:  # 确保只有一个维度为 1
                source_profile_2d = bd.squeeze(conversions.simE_to_worldE(source_profile), axis=squeeze_axis[0])
            else:
                raise ValueError("No single dimension found, or more than one dimension is 1")

            # 绘制 2D 颜色图
            im = axes[0][0].imshow(source_profile_2d, cmap="viridis", aspect="auto", origin="lower")
            # 添加颜色条
            plt.colorbar(im, ax=axes[0][0])
            # 设置标题和标签
            axes[0][0].set_title("Space distribution")
            if found_source.axis == "x":
                axes[0][0].set_xlabel("Y")
                axes[0][0].set_ylabel("Z")
            if found_source.axis == "y":
                axes[0][0].set_xlabel("X")
                axes[0][0].set_ylabel("Z")
            if found_source.axis == "z":
                axes[0][0].set_xlabel("X")
                axes[0][0].set_ylabel("Y")

        # 右侧子图: Time Signal 图
        time = bd.numpy(time)
        source_field = bd.numpy(source_field)
        if isinstance(found_source, fdtd.PlaneSource):
            axes[0][1].plot(time, source_field[:, int(shape[0] / 2), int(shape[1] / 2), int(shape[2] / 2), 0],
                            label="Ex")
            axes[0][1].plot(time, source_field[:, int(shape[0] / 2), int(shape[1] / 2), int(shape[2] / 2), 1],
                            label="Ey")
            axes[0][1].plot(time, source_field[:, int(shape[0] / 2), int(shape[1] / 2), int(shape[2] / 2), 2],
                            label="Ez")
        else:
            axes[0][1].plot(time, source_field[:, int(size / 2), 0], label="Ex")
            axes[0][1].plot(time, source_field[:, int(size / 2), 1], label="Ey")
            axes[0][1].plot(time, source_field[:, int(size / 2), 2], label="Ez")
        # axes[0][1].set_xticks()  # 每隔10个显示一个刻度
        axes[0][1].set_xlabel('fs')
        axes[0][1].set_ylabel("E (V/m)")
        axes[0][1].set_title(f"Time Signal of {source_name}")
        axes[0][1].legend()

        # Spectrum
        axes[1][0].plot(spectrum_freqs * 1e-12, spectrum)
        axes[1][0].set_xlabel('frequency (THz)')
        axes[1][0].set_ylabel(f"|E{conversions.number_to_letter(_Epol)}| (V/m)")
        axes[1][0].set_title(f"Spectrum of {source_name}")

        axes[1][1].plot(constants.c / spectrum_freqs * 1e6, spectrum)
        axes[1][1].set_xlabel('wavelength (um)')
        axes[1][1].set_ylabel(f"|E{conversions.number_to_letter(_Epol)}| (V/m)")
        axes[1][1].set_title(f"Spectrum of {source_name}")

        plt.tight_layout()

        file_name = "Source profile"
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))

        plt.close()

        return found_source, source_field, spectrum

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
        @return: None
        """

        if x == None:
            # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
            x = int(self._grid_xlength / 2)
        if y == None:
            y = int(self._grid_ylength / 2)
        if z == None:
            z = int(self._grid_zlength / 2)

        xlength, x, x_start, x_end = \
            self._handle_unit([xlength, x, x_start, x_end],
                              grid_spacing=self._grid.grid_spacing_x)
        ylength, y, y_start, y_end = \
            self._handle_unit([ylength, y, y_start, y_end],
                              grid_spacing=self._grid.grid_spacing_y)
        zlength, z, z_start, z_end = \
            self._handle_unit([zlength, z, z_start, z_end],
                              grid_spacing=self._grid.grid_spacing_z)
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
                z: z + zlength] = fdtd.BlockDetector(name=name, axis=axis)
            elif axis == "y":
                self._check_parameters(x, x + xlength, y, y, z, z + zlength, name=name)
                self._grid[x: x + xlength,
                y: y,
                z: z + zlength] = fdtd.BlockDetector(name=name, axis=axis)
            elif axis == "z":
                self._check_parameters(x, x + xlength, y, y + ylength, z, z, name=name)
                self._grid[x: x + xlength,
                y: y + ylength,
                z: z] = fdtd.BlockDetector(name=name, axis=axis)
        else:
            raise ValueError("Invalid detector type.")


    def _try_to_find_detector(self):
        """尝试在网格中找到一个监视器
        Try to find a detector in the grid.
        Returns:
            found_detector: the first detector found in the grid"""

        try:
            found_detector = self._grid.detectors[0]
            print("Found detector successfully without name")
            return found_detector
        except:
            raise Exception("No detector found in Grid.")

    def detector_profile(self, detector_name: str = None, field: str = "E", field_axis: str = "x", timesteps: int = -1):
        # 某一时刻的监视器场强分布，并保存为图片。没什么用
        # The field profile of a detector at a certain timestep, and save it as a picture. Quite useless.
        # TODO: block detector
        return
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
        x = bd.array(x) * self._grid.grid_spacing_x
        x_sticks = x
        field_number = conversions.letter_to_number(field_axis)
        detector_profile = bd.array([x for x in found_detector.detector_values()["%s" % field]])[timesteps, :,
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
                 geo=None,
                 show_structure=True,
                 show_energy=False):
        """
        Saving the geometry figure. This function can also show energy while show_energy = True.
        @param geo: Refractive index profile, will be calculated automatically if None. 也可以为None，程序会自己计算
        @param axis: axis to plot. 轴(若为二维XY模拟，则axis只能='z')
        @param axis_index: index of axis
        @param axis_number: an outdated version of axis_index
        @param animate: 是否生成动画。
        @param show_structure: 是否显示结构
        @param show_energy: 是否显示能量分布
        @return: None
        """
        if not axis:
            # Tell which dimension to draw automatically
            dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
            if not dims_with_size_one:
                axis = "y"
            else:
                axis = conversions.number_to_letter(dims_with_size_one[0])

        if axis_index is None:
            if axis_number is None:
                axis_index = int(self._grid.Ny / 2)
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
            self._grid.plot_structure(x=axis_index, save=True, animate=animate,
                                      index=index, folder=folder, geo=geo,
                                      background_index=self.background_index, show_structure=show_structure,
                                      show_energy=show_energy)
        elif axis == "y":
            self._grid.plot_structure(y=axis_index, save=True, animate=animate,
                                      index=index, folder=folder, geo=geo,
                                      background_index=self.background_index, show_structure=show_structure,
                                      show_energy=show_energy)
        elif axis == "z":
            self._grid.plot_structure(z=axis_index, save=True, animate=animate,
                                      index=index, folder=folder, geo=geo,
                                      background_index=self.background_index, show_structure=show_structure,
                                      show_energy=show_energy)
        else:
            raise ValueError("Unknown axis parameter.")

        plt.close()  # 清除画布

    def plot_n(self,
               axis: str = None,
               axis_index: int = 0,
               filepath: str = None):
        """
        Draw a refractive index plot. It is basically same with solve.plot().
        @param axis: axis to plot, can be 'x', 'y' or 'z'. If None, it will be automatically determined.
        @param axis_index: index of axis, default to 0.
        @param filepath: the path to save the figure. If None, it will be saved in the folder of the grid.
        @return: None
        """
        if not axis:
            # Tell which dimension to draw automatically
            dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
            if not dims_with_size_one:
                axis = "y"
                axis_index = int(self._grid.Ny / 2)
            else:
                axis = conversions.number_to_letter(dims_with_size_one[0])

        if not filepath:
            filepath = self.folder
        grid = self._grid
        geometry = bd.sqrt(1 / bd.to_float(grid.inverse_permittivity))
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
        n = bd.transpose(n, [1, 0, 2])

        if axis == "x":
            plt.xlabel('y/um')
            plt.ylabel('z/um')
            x_stick = x * grid.grid_spacing_y * 1e6
            y_stick = y * grid.grid_spacing_z * 1e6
        elif axis == "y":
            plt.xlabel('x/um')
            plt.ylabel('z/um')
            x_stick = x * grid.grid_spacing_x * 1e6
            y_stick = y * grid.grid_spacing_z * 1e6
        elif axis == "z":
            plt.xlabel('x/um')
            plt.ylabel('y/um')
            x_stick = x * grid.grid_spacing_x * 1e6
            y_stick = y * grid.grid_spacing_y * 1e6
        plt.imshow(bd.numpy(n[:, :, 0]), cmap=cm.jet, origin="lower",
                   extent=[0, x_stick, 0, y_stick])
        plt.clim([bd.min(n), bd.max(n)])
        plt.colorbar()
        plt.title("refractive_index_real")
        # 保存图片
        plt.savefig(fname='%s\\%s_%s=%d.png' % (filepath, 'index', axis, axis_index))

        # plt.show()
        plt.clf()
        plt.close()

    def run(self,
            time=None,
            save=True,
            animate: bool = False,
            interval=100
            ):
        """
        @param time: int for timesteps or float for seconds
        @param save: save the grid?
        @param animate: 是否生成动画？ ffmpeg required
        @param interval: 每隔多少个时间步保存一次图
        """
        if time is None:
            time = self._calculate_time()

        self._grid.animate = animate

        if not isinstance(time, int):
            time = self._grid._handle_time(time)
        print("The total time for FDTD simulation is %i timesteps or %f fs." % (
            time, time * self._grid.time_step * 1e15))
        self._grid.run(total_time=time, interval=interval)

        if save:
            self.save_simulation()
        if animate:
            self.animate()

    def animate(self,
                folder_path=None,
                output_video_path=None,
                fps=10):
        """
        使用 FFmpeg 将指定文件夹下的图片按文件名中的数字顺序生成视频。
        FFmpeg is required to generate video from images in the specified folder.
        Args:
            folder_path (str): 图片文件夹路径。
            output_video_path (str): 输出视频文件路径。
            fps (int): 视频帧率，默认为10。
        """
        import subprocess
        import re
        # 获取文件夹下的所有文件名
        if not folder_path:
            folder_path = self.folder + "/frames"
        if not output_video_path:
            output_video_path = self.folder + "/video.mp4"
        file_names = os.listdir(folder_path)

        # 定义提取数字的函数
        def extract_number(file_name):
            match = re.search(r'E_(\d+)\.png', file_name)
            return int(match.group(1)) if match else float('inf')

        # 按文件名中的数字排序
        sorted_file_names = sorted(file_names, key=extract_number)

        # 生成图片列表文件
        list_file_path = "image_list.txt"
        with open(list_file_path, "w") as f:
            for file_name in sorted_file_names:
                if file_name.startswith("E_") and file_name.endswith(".png"):
                    f.write(f"file '{os.path.join(folder_path, file_name)}'\n")

        # 构建 FFmpeg 命令
        command = [
            "ffmpeg",
            "-r", str(fps),
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_video_path
        ]

        # 执行 FFmpeg 命令
        subprocess.run(command)

        # 删除图片列表文件
        try:
            os.remove(list_file_path)
        except:
            print(f"Unalbe to remove {list_file_path}")

    def calculate_Transmission(self,
                               detector_name_1: str = None,
                               detector_name_2: str = None,
                               wl_start: float = None,
                               wl_end: float = None,
                               field_axis: str = "x",
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
        # Spectrum
        # TODO: Not finished yet. Not sure if the right way has been used. Or if it's not that complex?

        if grid is None:
            grid = self
        source, _, source_spectrum = self.source_data()

        # True先对坡印廷矢量傅里叶变换再积分
        # False: 先积分算功率再傅里叶变换
        integral_poynting = True
        if integral_poynting:
            for detector in grid._grid.detectors:
                if detector.name == detector_name_1:
                    P1 = detector.poynting[:, :, 2]
                    # P1[P1 > 0] = 0
                elif detector.name == detector_name_2:
                    P2 = detector.poynting[:, :, 2]
                    # P2[P2 > 0] = 0
            F1, F2 = bd.empty(shape=P1[0].shape, dtype=object), bd.empty(shape=P1[0].shape, dtype=object)
            for i in range(P1[0].shape[0]):
                fr = fdtd.FrequencyRoutines(self._grid, objs=P1[:, i])
                spectrum_freqs_1, fourier = fr.FFT(
                    freq_window_tuple=[source.frequency - source.bandwidth,
                                       source.frequency + source.bandwidth], )
                F1[i] = abs(fourier)
                fr = fdtd.FrequencyRoutines(self._grid, objs=P2[:, i])
                spectrum_freqs_2, fourier = fr.FFT(
                    freq_window_tuple=[source.frequency - source.bandwidth,
                                       source.frequency + source.bandwidth], )
                F2[i] = abs(fourier)
            spectrum_1 = bd.sum(F1, axis=0, keepdims=True)
            spectrum_2 = bd.sum(F2, axis=0, keepdims=True)
            Transmission = (spectrum_2 / spectrum_1)[0]
        else:
            for detector in grid._grid.detectors:
                if detector.name == detector_name_1:
                    flux_1 = detector.flux[:, 0, 2]
                elif detector.name == detector_name_2:
                    flux_2 = detector.flux[:, 0, 2]
            fr_1 = fdtd.FrequencyRoutines(grid._grid, objs=flux_1)
            spectrum_freqs_1, fourier_1 = fr_1.FFT(
                freq_window_tuple=[source.frequency - source.bandwidth,
                                   source.frequency + source.bandwidth], )
            fr_2 = fdtd.FrequencyRoutines(grid._grid, objs=flux_2)
            spectrum_freqs_2, fourier_2 = fr_2.FFT(
                freq_window_tuple=[source.frequency - source.bandwidth,
                                   source.frequency + source.bandwidth], )

            spectrum_1, spectrum_2 = abs(fourier_1), abs(fourier_2)
            Transmission = spectrum_2 / spectrum_1

            # # Power Spectrums
            fig, axes = plt.subplots(2, 2, figsize=(12, 6))  # 1行2列的子图

            axes[0][0].plot(bd.linspace(0, len(flux_1), len(flux_1)) * self._grid.time_step * 1e15, flux_1)
            axes[0][0].set_xlabel('fs')
            axes[0][0].set_ylabel('Power (W)')
            axes[0][0].set_title(f"Power of {detector_name_1}")

            axes[0][1].plot(bd.linspace(0, len(flux_1), len(flux_1)) * self._grid.time_step * 1e15, flux_2)
            axes[0][1].set_xlabel('fs')
            axes[0][1].set_ylabel('Power (W)')
            axes[0][1].set_title(f"Power of {detector_name_2}")

            axes[1][0].plot(spectrum_freqs_1, spectrum_1)
            axes[1][0].set_xlabel('frequency (THz)')
            axes[1][0].set_ylabel('Power (W)')
            axes[1][0].set_title(f"Power spectrum of {detector_name_1}")

            axes[1][1].plot(spectrum_freqs_2, spectrum_2)
            axes[1][1].set_xlabel('frequency (THz)')
            axes[1][1].set_ylabel('Power (W)')
            axes[1][1].set_title(f"Power spectrum of {detector_name_2}")

            plt.tight_layout()
            plt.savefig(os.path.join(grid.folder, f"Power_{detector_name_1}_{detector_name_2}.png"))
            plt.close()

        spectrum_wl = constants.c / (spectrum_freqs_1 * (1e-6))

        # Transmission Spectrums
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # 1行2列的子图

        axes[0].plot(conversions.wl_f_conversion((spectrum_wl)), Transmission)
        axes[0].set_xlabel('frequency (THz)')
        axes[0].set_ylabel('Normalized transmission')
        axes[0].set_title("Transmission")

        axes[1].plot(spectrum_wl, Transmission)
        axes[1].set_xlabel('wavelength (um)')
        axes[1].set_ylabel('Normalized transmission')
        axes[1].set_title("Transmission")

        plt.tight_layout()
        plt.savefig(os.path.join(grid.folder, f"Transmission_{detector_name_1}_{detector_name_2}.png"))
        plt.close()

        if save_to_txt:
            bd.savetxt('%s/Transmission.txt' % grid.folder, bd.column_stack((spectrum_wl, Transmission)), fmt='%f',
                       delimiter='\t',
                       header='Wavelength (um)\tTransmission', comments='')

    def calculate_Transmission_old(self,
                                   detector_name_1: str = None,
                                   detector_name_2: str = None,
                                   wl_start: float = None,
                                   wl_end: float = None,
                                   field_axis: str = "x",
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
        # Spectrum
        return
        field_axis = fdtd.conversions.letter_to_number(field_axis)
        if grid is None:
            grid = self
        for detector in grid._grid.detectors:
            if detector.name == detector_name_1:
                flux_1 = detector.flux[:, 0, 2]
            elif detector.name == detector_name_2:
                flux_2 = detector.flux[:, 0, 2]

        plt.plot(flux_1)
        plt.savefig(os.path.join(grid.folder, f"flux_1.png"))
        plt.close()
        plt.plot(flux_2)
        plt.savefig(os.path.join(grid.folder, f"flux_2.png"))
        plt.close()

        source = self._try_to_find_source()
        fr_1 = fdtd.FrequencyRoutines(grid._grid, objs=flux_1)
        spectrum_freqs_1, fourier_1 = fr_1.FFT(
            freq_window_tuple=[source.frequency - source.bandwidth,
                               source.frequency + source.bandwidth], )

        fr_2 = fdtd.FrequencyRoutines(grid._grid, objs=flux_2)
        spectrum_freqs_2, fourier_2 = fr_2.FFT(
            freq_window_tuple=[source.frequency - source.bandwidth,
                               source.frequency + source.bandwidth], )

        spectrum_1, spectrum_2 = abs(fourier_1), abs(fourier_2)

        spectrum_wl = constants.c / (spectrum_freqs_1 * (1e-6))
        Transmission = spectrum_2 / spectrum_1
        Transmission[Transmission > 1] = 1

        # 创建一个画布，包含两个子图
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # 1行2列的子图
        # Spectrum
        axes[0].plot(conversions.wl_f_conversion((spectrum_wl)), Transmission)
        axes[0].set_xlabel('frequency (THz)')
        axes[0].set_title("Transmission")

        axes[1].plot(spectrum_wl, Transmission)
        axes[1].set_xlabel('wavelength (um)')
        axes[1].set_title("Transmission")

        plt.tight_layout()
        plt.savefig(os.path.join(grid.folder, f"Transmission_{detector_name_1}_{detector_name_2}.png"))
        plt.close()

        if save_to_txt:
            bd.savetxt('%s/Transmission.txt' % grid.folder, bd.column_stack((spectrum_wl, Transmission)), fmt='%f',
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
        return
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
        for wl in bd.linspace(wl_start, wl_end, points):
            for attr in dir(self._grid):
                # 遍历grid的所有属性
                try:
                    if isinstance(getattr(self._grid, attr), fdtd.Object):
                        # 找到Object类型的属性并修改permittivity属性
                        getattr(self._grid, attr).permittivity[
                            getattr(self._grid, attr).permittivity != 1] = bd.square(index.fit_function_Reindex(wl))
                        # inverse_permittivity: 逆电容率（介电常数），即permittivity的倒数
                        getattr(self._grid, attr).inverse_permittivity[
                            getattr(self._grid, attr).inverse_permittivity != 1] = 1 / bd.square(
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

        # 保存detector_readings_sweep.bdz文件
        np.savez(os.path.join(self.folder, "detector_readings_sweep"), **dic)

    def _plot_sweep_result(self,
                           folder: str = ""):
        return
        # TODO: 完成它
        if folder == "":
            folder = self.folder

        for file_name in os.listdir(folder):
            if file_name.endswith('_sweep.npz'):
                # 识别_sweep.bdz文件
                # self.full_path = os.path.join(self.folder, file_name)
                self.calculate_T(full_path=os.path.join(folder, file_name))
        print(self.T)

        x = bd.linspace(self.wl_start, self.wl_end, self.points)

        # TODO: 除了光源监视器外只能设置一个监视器，只能看一个端口的透过率，完善它。
        plt.plot(x, self.T)
        plt.xlabel('Wavelength (μm)')
        plt.ylabel("T")
        plt.savefig(fname='%s//wl-%s.png' % (self.folder, "T"))
        plt.show()

    def _convert_tensors_to_numpy(self, obj, visited=None):
        """递归地将对象中的所有tensor转换为numpy数组，包括私有属性，避免循环引用
        Recursively convert all tensors in the object to numpy arrays,
        including private attributes, avoiding circular references.
        Args:

            """
        import torch

        # 初始化访问记录
        if visited is None:
            visited = set()

        # 检查对象ID，避免循环引用
        obj_id = id(obj)
        if obj_id in visited:
            return obj

        # 早期退出：如果是基本类型或np数组，直接返回
        if isinstance(obj, (str, int, float, bool, type(None), np.ndarray)):
            return obj

        # 检查是否是torch张量
        elif torch.is_tensor(obj):
            if obj.device.type == 'cuda':
                return obj.cpu().detach().numpy()
            else:
                return obj.detach().numpy()
        elif isinstance(obj, dict):
            # 只处理包含 tensor 的字典
            has_tensor = any(torch.is_tensor(v) or hasattr(v, '__dict__') for v in obj.values())
            if not has_tensor:
                return obj

            visited.add(obj_id)
            try:
                result = {key: self._convert_tensors_to_numpy(value, visited) for key, value in obj.items()}
                return result
            finally:
                visited.remove(obj_id)
        elif isinstance(obj, (list, tuple)):
            # 只处理包含 tensor 的列表/元组
            has_tensor = any(torch.is_tensor(item) or hasattr(item, '__dict__') for item in obj)
            if not has_tensor:
                return obj

            visited.add(obj_id)
            try:
                converted = [self._convert_tensors_to_numpy(item, visited) for item in obj]
                return type(obj)(converted)
            finally:
                visited.remove(obj_id)
        elif hasattr(obj, '__dict__'):
            visited.add(obj_id)
            try:
                # 只处理包含数据的属性
                for attr_name in list(obj.__dict__.keys()):
                    try:
                        attr_value = getattr(obj, attr_name)
                        # 跳过方法、类型和模块
                        if (not callable(attr_value) and
                                not isinstance(attr_value, (type, type(torch))) and
                                not attr_name.startswith('__')):

                            # 只有当属性值可能包含 tensor 时才递归处理
                            if (torch.is_tensor(attr_value) or
                                    isinstance(attr_value, (dict, list, tuple)) or
                                    hasattr(attr_value, '__dict__')):
                                converted_value = self._convert_tensors_to_numpy(attr_value, visited)
                                setattr(obj, attr_name, converted_value)

                    except (AttributeError, TypeError, RuntimeError, ValueError):
                        continue

                return obj
            finally:
                visited.remove(obj_id)
        else:
            return obj

    def save_simulation_old(self):
        """
        保存整个 Grid 的到npz.文件
        save the whole Grid to npz file.
        这个函数已经过时，建议使用 save_simulation() 函数。
        This function is deprecated, please use save_simulation() instead.
        """
        return

        # Serialize the class instance
        saved_grid = pickle.dumps(self)
        np.savez(os.path.join(self.folder, "saved_grid"), serialized_instance=saved_grid)

    def save_simulation(self):
        """使用 HDF5 格式保存grid，支持大型数据和压缩
        Use HDF5 format to save the grid, supporting large data and compression.
        保存时，tensor会被转为ndarray
        Tensors will be converted to ndarrays when saving.
        """
        import copy
        import gc
        from photfdtd.fdtd.backend import NumpyBackend

        # 使用 HDF5 保存大型数组数据
        grid_copy = copy.deepcopy(self)
        if bd.__class__ != NumpyBackend:
            # 如果不是 NumpyBackend，则将grid中的tensor转换为 ndarray
            grid_copy._convert_tensors_to_numpy(grid_copy)

        try:
            with h5py.File(os.path.join(self.folder, "saved_grid.h5"), 'w') as f:
                # 保存大型数组数据
                if hasattr(grid_copy._grid, 'E'):
                    f.create_dataset('E', data=grid_copy._grid.E, compression='gzip')
                    grid_copy._grid.E = None
                if hasattr(grid_copy._grid, 'H'):
                    f.create_dataset('H', data=grid_copy._grid.H, compression='gzip')
                    grid_copy._grid.H = None
                if hasattr(grid_copy._grid, 'inverse_permittivity'):
                    f.create_dataset('inverse_permittivity',
                                     data=grid_copy._grid.inverse_permittivity, compression='gzip')
                    grid_copy._grid.inverse_permittivity = None

                # 将剩余对象序列化
                metadata = pickle.dumps(grid_copy)

                # 处理大型序列化数据
                void_data = bd.void(metadata)
                if isinstance(void_data, bytes):
                    # 如果数据太大，保存为二进制数据集
                    f.create_dataset('metadata_bytes', data=np.frombuffer(void_data, dtype=np.uint8))
                else:
                    # 正常情况下保存为属性
                    f.attrs['metadata'] = void_data

        finally:
            del grid_copy
            gc.collect()

    @staticmethod
    def read_simulation_old(folder: str = None):
        """读取保存的grid
        静态方法，调用时应使用 data = Grid.read_simulation(folder="...")
        folder: 保存监视器数据的文件路径
        read the saved grid from a folder.
        这个函数已经过时，建议使用 read_simulation() 函数。
        This function is deprecated, please use read_simulation() instead.
        """
        return
        if not folder:
            raise Exception("Please indicate the folder where your grid has been saved")
        if not folder.endswith(".npz"):
            folder_bdz = folder + "\saved_grid.npz"
        try:
            readings = np.load(folder_bdz, allow_pickle=True)
        except:
            folder_bdz = folder + "\detector_readings.npz"
            readings = np.load(folder_bdz, allow_pickle=True)
        return pickle.loads(readings['serialized_instance'])

    @staticmethod
    def read_simulation(folder: str = None):
        """读取 HDF5 保存的数据
        read the saved grid from a folder using HDF5 format."""

        if not folder:
            raise ValueError("Folder path is required")

        h5_path = os.path.join(folder, "saved_grid.h5")
        if os.path.exists(h5_path):
            with h5py.File(h5_path, 'r') as f:
                # 恢复对象结构
                if 'metadata_bytes' in f:
                    # 从二进制数据集恢复
                    metadata_bytes = f['metadata_bytes'][...].tobytes()
                    grid_obj = pickle.loads(metadata_bytes)
                else:
                    # 从属性恢复
                    metadata = f.attrs['metadata']
                    if hasattr(metadata, 'tobytes'):
                        grid_obj = pickle.loads(metadata.tobytes())
                    else:
                        grid_obj = pickle.loads(metadata)

                # 恢复大型数据
                if 'E' in f:
                    grid_obj._grid.E = f['E'][...]
                if 'H' in f:
                    grid_obj._grid.H = f['H'][...]
                if 'inverse_permittivity' in f:
                    grid_obj._grid.inverse_permittivity = f['inverse_permittivity'][...]

            return grid_obj

        # 兼容旧格式
        npz_path = os.path.join(folder, "saved_grid.npz")
        if os.path.exists(npz_path):
            readings = np.load(npz_path, allow_pickle=True)
            return pickle.loads(readings['serialized_instance'])

        raise FileNotFoundError("No saved simulation found in the specified folder")

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
        print("Drawing dB map is not available currently.")
        return
        # FIXME: 由于detector数据保存方式的修改，该函数目前无法使用。需要读取h5文件
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
                fdtd.dB_map_2D(block_det=bd.array([x for x in detector.detector_values()["%s" % field]]),
                               interpolation=interpolation, axis=axis, field=field, field_axis=field_axis,
                               save=save, folder=folder, name_det=detector.name, total_time=total_time)

            # dic[detector.name + " (E)"] = bd.array([x for x in detector.detector_values()["E"]])
            # dic[detector.name + " (H)"] = bd.array([x for x in detector.detector_values()["H"]])
        # if block_det != None:
        #     data = block_det
        #     name_det = block_det.name
        # else:
        #     data = data[name_det + " (%s)" % field]

    @staticmethod
    def plot_field(grid=None, axis="y", axis_index=0, field="E", field_axis=None, folder=None, cmap="jet",
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
            title = "%s^2" % field
        else:
            title = f"{field}{field_axis}"
        if not folder:
            folder = grid.folder
        background_index = grid.background_index
        grid = grid._grid
        if not show_field:
            if axis == "z":
                field = bd.zeros_like(grid.E[:, :, axis_index, 0])
            elif axis == "y":
                field = bd.zeros_like(grid.E[:, axis_index, :, 0])
            elif axis == "x":
                field = bd.zeros_like(grid.E[axis_index, :, :, 0])
        else:
            if field == "E":
                if not field_axis:
                    # 能量
                    # TODO：这种算能量的方法对吗
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
                    # 能量
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
        if axis == "x":
            x_stick = field.shape[0] * grid.grid_spacing_y * 1e6
            y_stick = field.shape[1] * grid.grid_spacing_z * 1e6
        if axis == "y":
            x_stick = field.shape[0] * grid.grid_spacing_x * 1e6
            y_stick = field.shape[1] * grid.grid_spacing_z * 1e6
        if axis == "z":
            x_stick = field.shape[0] * grid.grid_spacing_x * 1e6
            y_stick = field.shape[1] * grid.grid_spacing_y * 1e6
        field = bd.numpy(field)
        plt.imshow(bd.transpose(field), vmin=vmin, vmax=vmax, cmap=cmap,
                   extent=[0, x_stick, 0, y_stick],
                   origin="lower")  # cmap 可以选择不同的颜色映射
        if show_field:
            cbar = plt.colorbar()
        if show_geometry:
            geo = bd.sqrt(1 / bd.to_float(grid.inverse_permittivity))

            # geo是四维矩阵，取最后一个维度
            geo = geo[:, :, :, -1]

            # 根据不同的轴选择截面
            if axis == "x":
                n_to_draw = geo[axis_index, :, :]
            elif axis == "y":
                n_to_draw = geo[:, axis_index, :]
            elif axis == "z":
                n_to_draw = geo[:, :, axis_index]

            # 创建轮廓数据
            contour_data = bd.where(n_to_draw != bd.array(background_index), 1, 0)

            plt.contour(
                bd.numpy(bd.linspace(0, x_stick, field.shape[0])),
                bd.numpy(bd.linspace(0, y_stick, field.shape[1])),
                bd.numpy(contour_data.T),
                colors='black', linewidths=1)

        # plt.ylim(-1, field.shape[1])
        # Make the figure full the canvas让画面铺满整个画布
        # plt.axis("tight")
        # 添加颜色条

        # cbar.set_label('')

        # 添加标题和坐标轴标签
        plt.title(f"{title}")

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
        Draw and save the field vs time of a point, no use currently. 绘制监视器某一点的时域场图 没什么用
        @param grid: Photfdtd.Grid
        @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
        @param data: read_simulation()读到的数据
        @param field_axis: x, y, z of E or H
        @param field: “E“或”H“
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 三维数组：用于面监视器，选择读取数据的点
        @param name_det: 监视器的名称
        """
        return
        data = None
        for detector in grid._grid.detectors:
            if detector.name == name_det:
                if field == "E":
                    data = bd.array(detector.real_E())
                elif field == "H":
                    data = bd.array(detector.real_H())
                else:
                    raise ValueError("Parameter field should be either 'E' or 'H")
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

    def read_detector(self, folder=None, name_det=None):
        """
        从保存监视器数据的路径读取监视器数据
        Read the detector data from the saved path.
        Args:
            folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
            name_det: The name of the detector to read. 监视器名称
        """
        if name_det is None:
            raise ValueError("Parameter name_det should not be None")
        if not folder:
            folder = self.folder
        E_path = f"{folder}\\{name_det}_E.h5"
        H_path = f"{folder}\\{name_det}_H.h5"

        # 打开 HDF5 文件
        for path in [E_path, H_path]:
            with h5py.File(path, "r") as f:
                # 打印文件中的所有数据集（类似于查看文件目录）
                def print_h5_structure(name, obj):
                    print(name, "->", obj)

                f.visititems(print_h5_structure)  # 遍历并打印 HDF5 文件结构

                # 读取某个数据集（假设文件中有 "E" 数据集）
                if "E" in f:
                    E = f["E"][:]  # 读取整个数据集
                    print("E shape:", E.shape)  # 打印数据形状
                    print("E dtype:", E.dtype)  # 打印数据类型
                elif "H" in f:
                    H = f["H"][:]  # 读取整个数据集
                    print("H shape:", H.shape)  # 打印数据形状
                    print("H dtype:", H.dtype)  # 打印数据类型

        return E, H

    def visualize_single_detector(self,
                                  detector=None,
                                  name_det=None,
                                  index=0,
                                  index_3d=None,
                                  field_axis="x",
                                  field="E"):
        """
        Visualization of the result of a single detector
        绘制单个监视器的结果
        @param detector: photfdtd.grid.detector
        @param name_det: 监视器名称
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 用于面监视器，选择读取数据的点
        @param field_axis: "x", "y", "z"
        @param field: ”E"或"H"
        @return frequency, spectrum: 频率和频谱
        关于傅里叶变换后的单位：有的人说是原单位，有的人说是原单位乘以积分时积的单位(s)
        https://stackoverflow.com/questions/1523814/units-of-a-fourier-transform-fft-when-doing-spectral-analysis-of-a-signal
        """
        # TODO: 把fdtd的fourier.py研究明白
        if field_axis is not None:
            # 如果field_axis是字母，转换为数字
            if field_axis in ["x", "y", "z"]:
                field_axis = conversions.letter_to_number(field_axis)
        if detector is None and name_det is not None:
            # 通过监视器名称找到监视器
            for d in self._grid.detectors:
                if d.name == name_det:
                    detector = d

        if name_det is None:
            name_det = detector.name

        if field == "E":
            data = self.read_detector(name_det)[0]
        elif field == "H":
            data = self.read_detector(name_det)[1]
        # if field == "E":
        #     data = bd.array(detector.real_E())
        # elif field == "H":
        #     data = bd.array(detector.real_H())
        else:
            raise ValueError("Parameter field should be either 'E' or 'H")
        data = bd.numpy(data)
        # if data is None:
        #     detector = self._grid.detectors[0]
        #     data = bd.array([x for x in detector.detector_values()["%s" % field]])

        shape = data.shape
        if data.ndim == 3:
            # 线监视器
            if not index:
                index = int(shape[1] / 2)
            indexed_data = data[:, index, field_axis]
        elif data.ndim == 5:
            # 面监视器
            if not index_3d:
                index_3d = [int(shape[1] / 2), int(shape[2] / 2), int(shape[3] / 2)]
            indexed_data = data[:, index_3d[0], index_3d[1], index_3d[2], field_axis]

        # Spectrum
        # TODO: consider multiple sources?考虑有不同光源的情况？
        source = self._try_to_find_source()
        fr = fdtd.FrequencyRoutines(self._grid, objs=indexed_data)
        spectrum_freqs, spectrum = fr.FFT(
            freq_window_tuple=[source.frequency - source.bandwidth,
                               source.frequency + source.bandwidth], )
        # spectrum是复值

        ### 试试ufdtd书中的方法，对空间中每个点的电场分别傅里叶变换
        # F = bd.empty(shape=data[0].shape, dtype=object)
        # for i in range(data[0].shape[0]):
        #     for j in range(3):
        #         fr = fdtd.FrequencyRoutines(self._grid, objs=data[:, i, j])
        #         spectrum_freqs, spectrum = fr.FFT(
        #             freq_window_tuple=[source.frequency - source.bandwidth,
        #                             source.frequency + source.bandwidth], )
        #         F[i, j] = abs(spectrum)
        ###

        # TODO: 目前只考虑了线监视器
        length = bd.numpy(bd.linspace(0, shape[1], shape[1]) * self._grid.grid_spacing_x)
        time = bd.numpy(bd.linspace(0, shape[0], shape[0]) * self._grid.time_step * 1e15)

        # 创建一个画布，包含两个子图
        fig, axes = plt.subplots(2, 2, figsize=(12, 6))  # 1行2列的子图

        # 左侧子图: Space distribution at when the field is maximum
        flattened_index = np.argmax(data)
        time_step_max_field = np.unravel_index(flattened_index, data.shape)[0]
        if data.ndim == 3:
            axes[0][0].plot(length * 1e6, data[time_step_max_field, :, field_axis])
            # axes[0][0].set_xticks()  # 每隔10个显示一个刻度
            axes[0][0].set_xlabel('um')
            axes[0][0].set_ylabel("E (V/m)")
            axes[0][0].set_title(f"Space distribution of {name_det} at {time_step_max_field * self._grid.time_step * 1e15} fs")
            axes[0][0].legend(["Detector profile"])
        elif data.ndim == 5:
            # 绘制 2D 颜色图
            im = axes[0][0].imshow(bd.transpose(bd.squeeze(data[time_step_max_field, :, :, :, field_axis])), cmap="viridis", aspect="auto", origin="lower")
            # 添加颜色条
            plt.colorbar(im, ax=axes[0][0])
            # 设置标题和标签
            axes[0][0].set_title("Space distribution")
            if detector.axis == "x":
                axes[0][0].set_xlabel("Y")
                axes[0][0].set_ylabel("Z")
            if detector.axis == "y":
                axes[0][0].set_xlabel("X")
                axes[0][0].set_ylabel("Z")
            if detector.axis == "z":
                axes[0][0].set_xlabel("X")
                axes[0][0].set_ylabel("Y")
            # axes[0][0].set_xticks()  # 每隔10个显示一个刻度
            axes[0][0].set_title(f"Space distribution of {name_det} at {time_step_max_field * self._grid.time_step * 1e15} fs")
            axes[0][0].legend(["Detector profile"])


        # 右侧子图: Time Signal 图
        if data.ndim == 3:
            axes[0][1].plot(time, data[:, index, 0], label="Ex")
            axes[0][1].plot(time, data[:, index, 1], label="Ey")
            axes[0][1].plot(time, data[:, index, 2], label="Ez")
        else:
            axes[0][1].plot(time, data[:, index_3d[0], index_3d[1], index_3d[2], 0], label="Ex")
            axes[0][1].plot(time, data[:, index_3d[0], index_3d[1], index_3d[2], 1], label="Ey")
            axes[0][1].plot(time, data[:, index_3d[0], index_3d[1], index_3d[2], 2], label="Ez")
        axes[0][1].set_xlabel('fs')
        axes[0][1].set_ylabel("E (V/m)")
        axes[0][1].set_title(f"Time Signal of {name_det}")
        axes[0][1].legend()

        # Spectrum
        axes[1][0].plot(spectrum_freqs * 1e-12, abs(spectrum))
        axes[1][0].set_xlabel('frequency (THz)')
        axes[1][0].set_ylabel(f"|E{conversions.number_to_letter(field_axis)}| (V/m)")
        axes[1][0].set_title(f"Spectrum of {name_det}")

        axes[1][1].plot(constants.c / spectrum_freqs * 1e6, abs(spectrum))
        axes[1][1].set_xlabel('wavelength (um)')
        axes[1][1].set_ylabel(f"|E{conversions.number_to_letter(field_axis)}| (V/m)")
        axes[1][1].set_title(f"Spectrum of {name_det}")

        plt.tight_layout()

        file_name = f"{name_det} profile"
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))

        plt.close()

        return spectrum_freqs * 1e-12, spectrum

    def visulize_detector(self,
                          field_axis="x",
                          field="E"):
        """
        绘制所有监视器的频谱。Draw the spectrum of all detectors.
        @param field_axis: "x", "y", "z"
        @param field: ”E"或"H"
        NOTE：
            This function will plot the spectrum of all detectors in the grid by
            using visualize_single_detector() for each one.
            这个函数使用 visualize_single_detector() 绘制网格中所有监视器的频谱。
        """
        # TODO: axis参数与其他可视化参数一致
        if field_axis is not None:
            field_axis = conversions.letter_to_number(field_axis)
        # spectrums = bd.empty(self._grid.detectors.shape)
        # names = bd.empty(self._grid.detectors.shape)
        for d in self._grid.detectors:
            freqs, spectrum = self.visualize_single_detector(detector=d, field=field, field_axis=field_axis)
            plt.plot(freqs, abs(spectrum), linestyle='-', label=d.name)
        source, __, spectrum_source = self.source_data()
        plt.plot(freqs, spectrum_source, linestyle='-', label=source.name)

        plt.ylabel('%s%s' % (field, conversions.number_to_letter(field_axis)))
        plt.xlabel("frequency (THz)")
        plt.title("Spectrum of detectors")
        plt.legend()
        file_name = "Spectrum of detectors"
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))
        plt.close()

    def slice_grid(self, grid=None, x_slice=[], y_slice=[], z_slice=[]):
        """
        切割grid，以切割后的grid创建grid_sliced
        Slice the grid to create a new grid_sliced.
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
                           grid_zlength=z_slice[1] - z_slice[0], grid_spacing=grid._grid.grid_spacing,
                           permittivity=self.background_index ** 2, foldername="%s_sliced_grid" % grid.folder)
        grid_sliced._grid.inverse_permittivity = grid._grid.inverse_permittivity[x_slice[0]:x_slice[1],
                                                 y_slice[0]:y_slice[1], z_slice[0]:z_slice[1]]

        return grid_sliced

    def visualize(self, axis: object = None, axis_index: int = None, field: str = "E", field_axis: str = None) -> None:
        """
        Generally visualize the grid, including field, energy, and detector data.
        可视化仿真结果，包括折射率分布，场分布，频谱和所有监视器结果。
        @param axis: axis to visualize, e.g., "x", "y", "z". If None, it will automatically detect.
        @param axis_index: int, the index of the axis to visualize. If None, it will be set to the middle of the axis.
        @param field: "E" or "H", the field to visualize. Default is "E".
        @param field_axis: str, the axis of the field to visualize, e.g., "x", "y", "z". If None, it will use the source's polarization.
        """
        # TODO: wl 能自动找到脉冲范围
        if axis is None:
            # 自动检测要绘制的维度
            dims_with_size_one = [i for i, size in enumerate(self._grid.inverse_permittivity.shape) if size == 1]
            axis = conversions.number_to_letter(dims_with_size_one[0] if dims_with_size_one else 1)

        axis_index = axis_index or self._grid.inverse_permittivity.shape[conversions.letter_to_number(axis)] // 2

        # 获取 source 数据
        for s in self._grid.sources:
            source, _, _ = self.source_data(source_name=s.name)

        # 获取 field_axis
        if field_axis is None:
            field_axis = getattr(source, "polarization", None)
            if field_axis is None:
                print("Grid.visualize: No source found in grid")

        self.save_fig(axis=axis, axis_index=axis_index)
        self.save_fig(axis=axis, axis_index=axis_index, show_energy=True)
        self.plot_n(axis=axis, axis_index=axis_index)
        self.plot_field(grid=self, field=field, field_axis=field_axis, axis=axis, axis_index=axis_index)

        if self._grid.detectors:  # 检查是否为空
            self.visulize_detector(field_axis=field_axis, field=field)

            for detector in self._grid.detectors:
                # self.detector_profile(detector_name=detector.name, field=field, field_axis=field_axis)
                # self.plot_fieldtime(grid=self, field=field, field_axis=field_axis, name_det=detector.name)
                if isinstance(detector, fdtd.detectors.BlockDetector):
                    self.dB_map(grid=self, field=field, field_axis=field_axis)
                # self.calculate_Transmission(detector_name=detector.name, source_name=self._try_to_find_source().name)
