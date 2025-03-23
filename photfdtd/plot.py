class Plot:
    def __init__(self):
        pass

    def visualize(self, axis=None, axis_index=None, field="E", field_axis=None):
        # TODO: wl 能自动找到脉冲范围
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
        for s in self._grid.sources:
            source, _, _ = self.source_data(source_name=s.name)

        if field_axis is None:
            try:
                field_axis = source.polarization
            except:
                print("Grid.visualize: No source found in grid")

        self.save_fig()
        self.save_fig(show_energy=True)
        self.plot_n()
        self.plot_field(grid=self, field=field, field_axis=field_axis, axis=axis, axis_index=axis_index)

        if self._grid.detectors:  # 检查是否为空
            self.visulize_detector(field_axis=field_axis, field=field)

            for detector in self._grid.detectors:
                self.detector_profile(detector_name=detector.name, field=field, field_axis=field_axis)
                self.plot_fieldtime(grid=self, field=field, field_axis=field_axis, name_det=detector.name)
                if isinstance(detector, fdtd.detectors.BlockDetector):
                    self.dB_map(grid=self, field=field, field_axis=field_axis)
                # self.calculate_Transmission(detector_name=detector.name, source_name=self._try_to_find_source().name)
    @staticmethod
    def plot_fieldtime(grid=None, folder=None, field_axis="z", field="E", index=None, index_3d=None, name_det=None):
        """
        Draw and save the field vs time of a point. 绘制监视器某一点的时域场图 没什么用
        @param grid: Photfdtd.Grid
        @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
        @param data: read_simulation()读到的数据
        @param field_axis: x, y, z of E or H
        @param field: “E“或”H“
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 三维数组：用于面监视器，选择读取数据的点
        @param name_det: 监视器的名称
        """
        pass
        data = None
        for detector in grid._grid.detectors:
            if detector.name == name_det:
                if field == "E":
                    data = np.array(detector.real_E())
                elif field == "H":
                    data = np.array(detector.real_H())
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


    def read_detector(self, name_det=None):
        """
        读取监视器数据
        @param name_det: 监视器名称
        @param field: "E"或"H"
        """
        import h5py
        E_path = f"{self.folder}\\{name_det}_E.h5"
        H_path = f"{self.folder}\\{name_det}_H.h5"

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
                                  index_3d=[0, 0, 0],
                                  field_axis="x",
                                  field="E"):
        """
        Visualization of the result of a single detector
        @param detector: photfdtd.grid.detector
        @param name_det: 监视器名称
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 用于面监视器，选择读取数据的点
        @param field_axis: "x", "y", "z"
        @param field: ”E"或"H"
        NOTE：
            关于傅里叶变换后的单位：有的人说是原单位，有的人说是原单位乘以积分时积的单位(s)
            https://stackoverflow.com/questions/1523814/units-of-a-fourier-transform-fft-when-doing-spectral-analysis-of-a-signal
        """
        # TODO: axis参数与其他可视化参数一致
        # TODO: 把fdtd的fourier.py研究明白
        if field_axis is not None:
            field_axis = conversions.letter_to_number(field_axis)
        if detector is None and name_det is not None:
            for d in self._grid.detectors:
                if d.name == name_det:
                    detector = d

        if field == "E":
            data = self.read_detector(detector.name)[0]
        elif field == "H":
            data = self.read_detector(detector.name)[1]
        # if field == "E":
        #     data = np.array(detector.real_E())
        # elif field == "H":
        #     data = np.array(detector.real_H())
        else:
            raise ValueError("Parameter field should be either 'E' or 'H")
        # if data is None:
        #     detector = self._grid.detectors[0]
        #     data = np.array([x for x in detector.detector_values()["%s" % field]])
        if data is None:
            raise ValueError("No detector found in Grid")
        shape = data.shape
        if data.ndim == 3:
            if not index:
                index = int(shape[1] / 2)
            indexed_data = data[:, index, field_axis]
        elif data.ndim == 5:
            if not index_3d:
                index_3d = [int(shape[0] / 2), int(shape[1] / 2), int(shape[2] / 2)]
            indexed_data = data[:, index_3d[0], index_3d[1], index_3d[2], field_axis]

        # Spectrum
        # TODO: consider multiple sources?考虑有不同光源的情况？
        source = self._try_to_find_source()
        fr = fdtd.FrequencyRoutines(self._grid, objs=indexed_data)
        spectrum_freqs, fourier = fr.FFT(
            freq_window_tuple=[source.frequency - 2 * source.bandwidth,
                               source.frequency + 2 * source.bandwidth], )
        spectrum = abs(fourier)

        ### 试试ufdtd书中的方法，对空间中每个点的电场分别傅里叶变换
        # F = np.empty(shape=data[0].shape, dtype=object)
        # for i in range(data[0].shape[0]):
        #     for j in range(3):
        #         fr = fdtd.FrequencyRoutines(self._grid, objs=data[:, i, j])
        #         spectrum_freqs, fourier = fr.FFT(
        #             freq_window_tuple=[source.frequency - 2 * source.bandwidth,
        #                             source.frequency + 2 * source.bandwidth], )
        #         F[i, j] = abs(fourier)
        ###

        # TODO: 目前只考虑了线监视器
        length = np.linspace(0, shape[1], shape[1]) * self._grid.grid_spacing_x
        time = np.linspace(0, shape[0], shape[0]) * self._grid.time_step * 1e15

        # 创建一个画布，包含两个子图
        fig, axes = plt.subplots(2, 2, figsize=(12, 6))  # 1行2列的子图

        # 左侧子图: 源 Profile 图
        axes[0][0].plot(length * 1e6, data[-1, :, field_axis])
        # axes[0][0].set_xticks()  # 每隔10个显示一个刻度
        axes[0][0].set_xlabel('um')
        axes[0][0].set_ylabel("E")
        axes[0][0].set_title(f"Space distribution of {detector.name} at {self._grid.time_passed * 1e15} fs")
        axes[0][0].legend(["Detector profile"])

        # 右侧子图: Time Signal 图
        axes[0][1].plot(time, data[:, index, 0], label="Ex")
        axes[0][1].plot(time, data[:, index, 1], label="Ey")
        axes[0][1].plot(time, data[:, index, 2], label="Ez")
        axes[0][1].set_xlabel('fs')
        axes[0][1].set_ylabel("E")
        axes[0][1].set_title(f"Time Signal of {detector.name}")
        axes[0][1].legend()

        # Spectrum
        axes[1][0].plot(spectrum_freqs * 1e-12, spectrum)
        axes[1][0].set_xlabel('frequency (THz)')
        axes[1][0].set_ylabel("E")
        axes[1][0].set_title(f"Spectrum of {detector.name}")

        axes[1][1].plot(constants.c / spectrum_freqs * 1e6, spectrum)
        axes[1][1].set_xlabel('wavelength (um)')
        axes[1][1].set_ylabel("E")
        axes[1][1].set_title(f"Spectrum of {detector.name}")

        plt.tight_layout()

        file_name = f"{detector.name} profile"
        plt.savefig(os.path.join(self.folder, f"{file_name}.png"))

        plt.close()

        return spectrum_freqs * 1e-12, spectrum


    def visulize_detector(self,
                          index=0,
                          index_3d=[0, 0, 0],
                          field_axis="x",
                          field="E"):
        """
        傅里叶变换绘制频谱
        @param wl_start: 起始波长(m)
        @param wl_end: 结束波长(m)
        @param name_det: 监视器名称
        @param input_data: Optional: 如果输入了这个数据，则data、name_det、index、index_3d可以不输入。input_data必须是一个一维数组，
        其长度表示时间步长，每一个元素表示在该时间场的幅值。
        @param index: 用于线监视器，选择读取数据的点
        @param index_3d: 用于面监视器，选择读取数据的点
        @param field_axis: "x", "y", "z"
        @param field: ”E"或"H"
        NOTE：
            关于傅里叶变换后的单位：有的人说是原单位，有的人说是原单位乘以积分时积的单位(s)
            https://stackoverflow.com/questions/1523814/units-of-a-fourier-transform-fft-when-doing-spectral-analysis-of-a-signal
        """
        # TODO: axis参数与其他可视化参数一致
        # TODO: 把fdtd的fourier.py研究明白
        if field_axis is not None:
            field_axis = conversions.letter_to_number(field_axis)
        # spectrums = np.empty(self._grid.detectors.shape)
        # names = np.empty(self._grid.detectors.shape)
        for d in self._grid.detectors:
            freqs, spectrum = self.visualize_single_detector(detector=d)
            plt.plot(freqs, spectrum, linestyle='-', label=d.name)
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
                           grid_zlength=z_slice[1] - z_slice[0], grid_spacing=grid._grid.grid_spacing,
                           permittivity=self.background_index ** 2, foldername="%s_sliced_grid" % grid.folder)
        grid_sliced._grid.inverse_permittivity = grid._grid.inverse_permittivity[x_slice[0]:x_slice[1],
                                                 y_slice[0]:y_slice[1], z_slice[0]:z_slice[1]]

        return grid_sliced



