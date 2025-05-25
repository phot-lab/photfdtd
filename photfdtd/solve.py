# import utils
import photfdtd.philsol as ps
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from os import path
import photfdtd.fdtd as fdtd


class Solve:
    """
    绘制二维截面、计算波导模式，通过加入philsol包实现 https://github.com/philmain28/philsol
    # TODO:似乎有更好的库来代替philsol？
    """

    def __init__(self,
                 grid: fdtd.grid,
                 axis: str = 'x',
                 axis_index: int = None,
                 index: int = 0,
                 filepath: str = None

                 ):
        '''
        23.03.18
        本函数除了作为__init__函数，其主要功能是将fdtd.grid变量及其内部保存的waveguide映射到矩阵self.geometry中。
        self.geometry是一个四维矩阵 [x,y,z,3]，这是因为对于各向异性材料，它们在x，y，z三个方向上折射率不同，所以需要四维才能表现。
        但暂时还不能编辑各向异性材料
        :param grid: fdtd.grid
        :param: axis: 哪个轴的截面
        :param: axis_index/index: index of the axis choosed 轴上哪点
        :param: filepath: 保存图片的文件夹
        '''
        if axis_index:
            index = axis_index
        if not filepath:
            filepath = grid.folder
        self.grid = grid._grid
        self.geometry = np.sqrt(1 / np.float16(self.grid.inverse_permittivity))
        # for i in range(len(self.grid.objects)):
        #     self.geometry[self.grid.objects[i].x.start:self.grid.objects[i].x.stop,
        #     self.grid.objects[i].y.start:self.grid.objects[i].y.stop,
        #     self.grid.objects[i].z.start:self.grid.objects[i].z.stop] = np.sqrt(self.grid.objects[i].permittivity)

        self.axis = axis.lower()
        self.index = index
        self.filepath = filepath


        # 去掉作为轴的那一维
        if axis == 'x':
            self.n = self.geometry[index, :, :, :]
        elif axis == 'y':
            self.n = self.geometry[:, index, :, :]
        elif axis == 'z':
            self.n = self.geometry[:, :, index, :]
        else:
            raise ValueError('Parameter "axis" should be x, y or z! ')

        # 日后加入判断是否是各向异性材料

    def plot(self, image_name=None):
        """
        绘制截面折射率分布图。
        # TODO:如果要仿真各向异性材料，代码还需要更加细化
        :return: None
        """

        self.x = self.n.shape[0]
        self.y = self.n.shape[1]

        # It's quite important to transpose n
        self.n = np.transpose(self.n, [1, 0, 2])
        plt.imshow(self.n[:, :, 0], cmap=cm.jet, origin="lower",
                   extent=[0, self.x * self.grid.grid_spacing * 1e6, 0, self.y * self.grid.grid_spacing * 1e6])
        # plt.axis("tight")
        plt.clim([np.amin(self.n), np.amax(self.n)])
        # plt.xlim((0, self.n.shape[0] * self.grid.grid_spacing * 1e6))
        # plt.ylim((0, self.n.shape[1] * self.grid.grid_spacing * 1e6))
        if self.axis == "x":
            plt.xlabel('y/um')
            plt.ylabel('z/um')
        elif self.axis == "y":
            plt.xlabel('x/um')
            plt.ylabel('z/um')
        elif self.axis == "z":
            plt.xlabel('x/um')
            plt.ylabel('y/um')
        plt.colorbar()
        plt.title("refractive_index_real")
        # 保存图片
        # 判断 image_name 是否为 None
        if image_name is None:
             image_name = '%s_%s=%d.png' % ('index', self.axis, self.index)  # 默认命名方式
        else:
             image_name = '%s\\%s' % (self.filepath, image_name)  # 使用传入的 filename
        plt.savefig(fname=image_name)

        # plt.show()
        plt.clf()
        plt.close()




    def calculate_mode(self,
                       lam: float = 1550e-9,
                       neff: float = None,
                       neigs: int = 1,
                       x_boundary_low=None, y_boundary_low=None,
                       x_boundary_high=None, y_boundary_high=None,
                       x_thickness_low: int or float = None, y_thickness_low: int or float = None,
                       x_thickness_high: int or float = None, y_thickness_high: int or float = None,
                       background_index=None
                       ):
        """
        调用phisol包，计算模式
        @param lam: 波长（m）
        @param neff: 在neff周围计算模式
        @param neigs: 计算模式数
        @param x_boundary_low: "pml"或"zero"，分别表示pml或零值边界
        @param y_boundary_low:
        @param x_thickness_low: int表示pml边界的厚度
        @param y_thickness_low:
        @param x_boundary_high:
        @param y_boundary_high:
        @param x_thickness_high:
        @param y_thickness_high:
        @return:
        """
        if background_index == None:
            # If background_index not given, it will be min(self.n) which is not right in some cases (like photonic crystal)
            background_index = np.amin(self.n)
        # NOTE: fdtd的单位是m，而philsol的单位是um
        if neff == None:
            neff = np.max(self.n)
        self.lam = lam * 10 ** 6
        self.k = 2 * np.pi / self.lam
        PML_with = int(np.round(lam / self.grid.grid_spacing / 4))
        if x_boundary_low == "pml" and not x_thickness_low:
            x_thickness_low = PML_with
        if x_boundary_high == "pml" and not x_thickness_high:
            x_thickness_high = PML_with
        if y_boundary_low == "pml" and not y_thickness_low:
            y_thickness_low = PML_with
        if y_boundary_high == "pml" and not y_thickness_high:
            y_thickness_high = PML_with
        try:
            if self.axis == "x":
                x_thickness_low, x_thickness_high, y_thickness_low, y_thickness_high = \
                    self.grid._handle_distance(x_thickness_low, "y"), self.grid._handle_distance(x_thickness_high, "y"), \
                    self.grid._handle_distance(y_thickness_low, "z"), self.grid._handle_distance(y_thickness_high, "z"),
            if self.axis == "y":
                x_thickness_low, x_thickness_high, y_thickness_low, y_thickness_high = \
                    self.grid._handle_distance(x_thickness_low, "x"), self.grid._handle_distance(x_thickness_high, "x"), \
                    self.grid._handle_distance(y_thickness_low, "z"), self.grid._handle_distance(y_thickness_high, "z"),
            if self.axis == "z":
                x_thickness_low, x_thickness_high, y_thickness_low, y_thickness_high = \
                    self.grid._handle_distance(x_thickness_low, "x"), self.grid._handle_distance(x_thickness_high, "x"), \
                    self.grid._handle_distance(y_thickness_low, "y"), self.grid._handle_distance(y_thickness_high, "y"),
        except:
            pass
        print(x_thickness_low, x_thickness_high, y_thickness_low, y_thickness_high)
        # Calculate modes
        # FIXME: 检查pml边界的四个方向是否有问题
        P, matrices = ps.eigen_build(self.k, self.n, self.grid.grid_spacing * 1e6, self.grid.grid_spacing * 1e6,
                                     x_boundary_low=x_boundary_low, y_boundary_low=y_boundary_low,
                                     x_thickness_low=x_thickness_low,
                                     y_thickness_low=y_thickness_low, x_boundary_high=x_boundary_high,
                                     y_boundary_high=y_boundary_high, x_thickness_high=x_thickness_high,
                                     y_thickness_high=y_thickness_high, background_index=background_index)
        beta_in = 2. * np.pi * neff / self.lam
        self.beta, Ex_field, Ey_field = ps.solve.solve(P, beta_in, neigs=neigs)

        flag_deleted = []
        print("%i modes are found" % neigs)
        print("neff=", self.beta * self.lam / (2 * np.pi))

        # Discard dispersion modes 丢掉耗散模
        for i in range(len(self.beta)):
             print(abs(self.beta[i].imag * self.lam / (2 * np.pi)))
             if abs(self.beta[i].imag * self.lam / (2 * np.pi)) > 1e-5:
                 flag_deleted.append(i)
                 neigs -= 1

        self.beta, Ex_field, Ey_field = np.delete(self.beta, flag_deleted), \
                                        np.delete(Ex_field, flag_deleted, 0), \
                                        np.delete(Ey_field, flag_deleted, 0)
        print("%i dispersion modes have been discarded" % len(flag_deleted))

        self.effective_index = self.beta * self.lam / (2 * np.pi)
        print("neff=", self.effective_index)

        # Now calculate the other fields
        Hx = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
        Hy = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
        Hz = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

        if self.axis == 'x':
            Ex = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

            for i in range(neigs):
                Ex[i], Hy[i], Hz[i], Hx[i] = ps.construct.extra_feilds(k0=self.k, beta=self.beta[i],
                                                                       Ex=Ex_field[i], Ey=Ey_field[i],
                                                                       matrices=matrices)
            Ex = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ex]
            Ey = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ex_field]
            Ez = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ey_field]


        elif self.axis == 'y':

            Ey = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

            for i in range(neigs):
                Ey[i], Hx[i], Hz[i], Hy[i] = ps.construct.extra_feilds(k0=self.k, beta=self.beta[i],
                                                                       Ex=Ex_field[i], Ey=Ey_field[i],
                                                                       matrices=matrices)

            Ey = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ey]
            Ex = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ex_field]
            Ez = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ey_field]


        elif self.axis == 'z':

            Ez = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

            for i in range(neigs):
                Ez[i], Hx[i], Hy[i], Hz[i] = ps.construct.extra_feilds(k0=self.k, beta=self.beta[i], Ex=Ex_field[i],
                                                                       Ey=Ey_field[i], matrices=matrices)
            # (self.x, self.y)
            Ez = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ez]
            Ex = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ex_field]
            Ey = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Ey_field]

        Hx = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Hx]
        Hy = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Hy]
        Hz = [np.reshape(E_vec, (self.x, self.y)) for E_vec in Hz]

        dic = {"number_of_modes": neigs, "axis": self.axis,"grid_spacing": self.grid.grid_spacing, "lam": lam,
               "effective_index": self.effective_index,  "Ex": Ey, "Ey": Ex, "Ez": Ez, "Hx": Hy, "Hy": Hx,
               "Hz": Hz}

        # 似乎原代码中Ex, Ey和Hx, Hy弄反了，所以我在这里调换了一下

        return dic

    @staticmethod
    def draw_mode(filepath,
                  data: dict = None,
                  content: str = "amplitude",
                  number:int=0,
                  TE_fractions=None
                  ) -> None:
        '''
        绘制模式，保存图片与相应的有效折射率
        :param neigs: 绘制模式数
        :param component: ey: 绘制Ey ex: 绘制Ex # TODO: Ez与磁场？
        :param TE_fractions: TE分量的比值列表
        :return: None
        '''
        axis = data["axis"]
        effective_index = data["effective_index"]
        grid_spacing = data["grid_spacing"]
        lam = data["lam"]
        # plot mode figures
        for j in ("Ex", "Ey", "Ez", "Hx", "Hy", "Hz"):
            for i in range(data["number_of_modes"]):  # For each eigenvalue
                plt.figure()
                if content == "real_part":
                    plot_matrix = np.transpose(data[j][i].real)
                elif content == "amplitude":
                    plot_matrix = np.transpose(abs(data[j][i]))
                elif content == "imaginary_part":
                    plot_matrix = np.transpose(data[j][i].imag)
                elif content == "phase":
                    plot_matrix = np.transpose(np.angle(data[j][i]))

                plt.imshow(plot_matrix, cmap=cm.jet, origin="lower",
                           # 由于做了转置，所以这里要交换x， y
                           extent=[0, plot_matrix.shape[1] * grid_spacing * 1e6,
                                   0, plot_matrix.shape[0] * grid_spacing * 1e6])
                # plt.axis("tight")
                plt.clim([np.amin(plot_matrix), np.amax(plot_matrix)])
                plt.colorbar()
                if axis == "x":
                    plt.xlabel('y/um')
                    plt.ylabel('z/um')
                elif axis == "y":
                    plt.xlabel('x/um')
                    plt.ylabel('z/um')
                elif axis == "z":
                    plt.xlabel('x/um')
                    plt.ylabel('y/um')
                formatted_neff = "{:.6f}".format(effective_index[i])
                plt.title('%s_of_%s\n neff=%s' % (content, j, str(formatted_neff)))
                # 保存图片
                plt.tight_layout()
                plt.savefig(fname='%s\\%s%d_%s_%s.png' % (filepath, 'mode', i + 1, content, j))
                plt.close()

        # Draw E/H intensity
        for i in range(data["number_of_modes"]):
            if axis == "x":
                E_intensity = data["Ey"][i].real ** 2 + data["Ez"][i].real ** 2
                H_intensity = data["Hy"][i].real ** 2 + data["Hz"][i].real ** 2
                Ex = data["Ey"][i].real
                Ey = data["Ez"][i].real
            if axis == "y":
                E_intensity = data["Ex"][i].real ** 2 + data["Ez"][i].real ** 2
                H_intensity = data["Hx"][i].real ** 2 + data["Hz"][i].real ** 2
                Ex = data["Ex"][i].real
                Ey = data["Ez"][i].real
            if axis == "z":
                E_intensity = data["Ex"][i].real ** 2 + data["Ey"][i].real ** 2
                H_intensity = data["Hx"][i].real ** 2 + data["Hy"][i].real ** 2
                Ex = data["Ex"][i].real
                Ey = data["Ey"][i].real
            # 转置以匹配图像绘制的方式
            E_intensity = np.transpose(E_intensity)
            H_intensity = np.transpose(H_intensity)
            Ex = np.transpose(Ex)
            Ey = np.transpose(Ey)
            # 绘制E强度图
            plt.figure()
            plt.imshow(E_intensity, cmap=cm.jet, origin="lower",
                       # 由于做了转置，所以这里要交换x， y
                       extent=[0, E_intensity.shape[1] * grid_spacing * 1e6,
                               0, E_intensity.shape[0] * grid_spacing * 1e6])
            plt.clim([np.amin(E_intensity), np.amax(E_intensity)])
            plt.colorbar()
            if axis == "x":
                plt.xlabel('y/um')
                plt.ylabel('z/um')
            elif axis == "y":
                plt.xlabel('x/um')
                plt.ylabel('z/um')
            elif axis == "z":
                plt.xlabel('x/um')
                plt.ylabel('y/um')
            #设置标题
            mode_type = "(TE)" if TE_fractions and TE_fractions[i] >= 0.55 else "(TM)"
            plt.title(f'E_intensity {mode_type}\nneff={effective_index[i]}')


            # 计算电场强度的最大值
            max_intensity = np.amax(E_intensity)
            # 使用最大值的 10% 作为阈值，可以根据需要调整这个比例
            threshold = 0.1 * max_intensity
            # 计算电场不为零的区域
            non_zero_region = np.where(E_intensity >threshold)  # 找到电场强度大于某个阈值的区域
            # 检查数组是否为空，以避免后续报错
            if non_zero_region[0].size == 0:
               print(f"Mode {i}: No regions with sufficient E_intensity.")
               continue
            # 计算电场不为零区域的边界
            min_y, max_y = np.min(non_zero_region[0]), np.max(non_zero_region[0])
            min_x, max_x = np.min(non_zero_region[1]), np.max(non_zero_region[1])
            # 生成箭头放置的点
            x_points = np.linspace(min_x, max_x, int(np.sqrt(number)), dtype=int)
            y_points = np.linspace(min_y, max_y, int(np.sqrt(number)), dtype=int)
            # 确定最大箭头长度和宽度，并确保矩形波导和光纤箭头的一致性
            fixed_grid_points = 125#固定的网格点
            if grid_spacing<100e-9:
                arrow_length = fixed_grid_points * grid_spacing * 6e4
            elif grid_spacing>400e-9:
                arrow_length = fixed_grid_points * grid_spacing * 2e5
            else:
                arrow_length = fixed_grid_points * grid_spacing * 8e4
            max_arrow_scale = 1 / arrow_length#确保max_arrow_scale = 0.08
            max_arrow_width = 0.008
            # 绘制均匀间隔的矢量箭头
            for y in y_points:
                for x in x_points:
                    Ex_val = Ex[y, x]
                    Ey_val = Ey[y, x]
                    magnitude = np.sqrt(Ex_val**2 + Ey_val**2)

                    if E_intensity[y, x] > threshold:
                        # 根据相对电场强度比例调整箭头长度和宽度
                        relative_intensity = E_intensity[y, x] / max_intensity
                        arrow_scale = max_arrow_scale / relative_intensity if relative_intensity > 0 else max_arrow_scale
                        arrow_width = max_arrow_width * relative_intensity
                        #print("arrow_scale:", arrow_scale, "arrow_width:", arrow_width)
                        if magnitude > 0:
                            Ex_val_normalized = Ex_val / magnitude
                            Ey_val_normalized = Ey_val / magnitude
                        else:
                            Ex_val_normalized = 0
                            Ey_val_normalized = 0

                        #绘制箭头，scale掌管箭头整体长度，width掌管箭头宽度
                        plt.quiver(x * grid_spacing * 1e6, y * grid_spacing * 1e6,
                                    Ex_val_normalized,Ey_val_normalized,
                                    angles='xy', scale_units='xy',scale=arrow_scale,width=arrow_width,
                                    color='white', pivot='middle')


            # 保存图片
            plt.savefig(fname='%s\\%s%d_E_intensity.png' % (filepath, 'mode', i + 1))
            plt.close()

            # 绘制H强度图
            plt.figure()
            plt.imshow(H_intensity, cmap=cm.jet, origin="lower",
                       # 由于做了转置，所以这里要交换x， y
                       extent=[0, H_intensity.shape[1] * grid_spacing * 1e6,
                               0, H_intensity.shape[0] * grid_spacing * 1e6])
            plt.clim([np.amin(H_intensity), np.amax(H_intensity)])
            plt.colorbar()
            if axis == "x":
                plt.xlabel('y/um')
                plt.ylabel('z/um')
            elif axis == "y":
                plt.xlabel('x/um')
                plt.ylabel('z/um')
            elif axis == "z":
                plt.xlabel('x/um')
                plt.ylabel('y/um')
            plt.title('H_intensity\nneff=%s' % (str(effective_index[i])))
            # 保存图片
            plt.savefig(fname='%s\\%s%d_H_intensity.png' % (filepath, 'mode', i + 1))
            plt.close()


    @staticmethod
    def save_mode(folder, dic, index: int = None, format: str = "npz"):
        """
        Save result
        @param folder: folder path to save data
        @param dic: dic from calculate_mode()
        @param index: mode index to save
        @param format: "npz" or "txt"
        """
        # 保存计算的模式
        if not index:
            data = dic
            if format == "npz":
                np.savez(path.join(folder, "saved_modes"), **data)
            elif format == "txt":
                # 打开文件，以写入模式打开，如果文件不存在则创建
                import os
                filepath = folder + "/saved_modes.txt"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                # 将字典的键和值转换为列表
                keys = list(data.keys())
                values = list(data.values())

                # 创建一个 NumPy 数组，保存键和值
                data = np.array([keys, values], dtype=object).T
                np.set_printoptions(threshold=np.inf)
                # 保存为文本文件
                np.savetxt(filepath, data, fmt='%s')
                np.set_printoptions()
                print("txt has been saved")
        elif index:
            # 字典是可变对象，在函数内部修改dic会同时修改函数外的dic
            data = {}
            for i in ("number_of_modes", "axis", "grid_spacing", "lam"):
                data[i] = dic[i]
            for i in ("effective_index", "Ex", "Ey", "Ez", "Hx", "Hy", "Hz"):
                data[i] = dic[i][index]


            if format == "npz":
                np.savez(path.join(folder, "saved_modes"), **data)
            elif format == "txt":
                # 打开文件，以写入模式打开，如果文件不存在则创建
                import os
                filepath = folder + "/saved_modes.txt"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                # 将字典的键和值转换为列表
                keys = list(data.keys())
                values = list(data.values())

                # 创建一个 NumPy 数组，保存键和值
                data = np.array([keys, values], dtype=object).T
                np.set_printoptions(threshold=np.inf)
                # 保存为文本文件
                np.savetxt(filepath, data, fmt='%s')
                np.set_printoptions()
                print("txt has been saved")


    @staticmethod
    def read_mode(folder):
        if not folder.endswith("saved_modes.npz"):
            folder = folder + "\\saved_modes.npz"
        readings = np.load(folder, allow_pickle=True)
        names = readings.files
        data = {}
        i = 0
        for name in names:
            data[name] = readings[name]
            i += 1
        return data

    def calculate_TEfraction(self,
                             dic,
                             axis,
                             n_levels: int = 6,
                             ) -> None:
        """
        绘制不同模式的Ey与Ex的实部之比，并保存
        # TODO: 在lumerical中，TE fracttion 来自全区域电场的平方积分之比，得到的是一个数，并不是这种算法。是否需要改正？
        :param filepath: 保存图片路径
         n_levels：需要计算模式TE的个数
        :return: None
        """
        # 根据 axis 选择合适的电场分量
        if axis == 'x':
            # 传播方向为 x，横截面电场为 Ey 和 Ez
            Ey_list = dic["Ey"]
            Ez_list = dic["Ez"]
            Ex_list = dic["Ex"]  # 不忽略 Ex 分量
        elif axis == 'y':
            # 传播方向为 y，横截面电场为 Ex 和 Ez
            Ex_list = dic["Ex"]
            Ez_list = dic["Ez"]
            Ey_list = dic["Ey"]

        elif axis == 'z':
            # 传播方向为 z，横截面电场为 Ex 和 Ey
            Ex_list = dic["Ex"]
            Ey_list = dic["Ey"]
            Ez_list = dic["Ez"]
         # 获取网格的横截面积,仅适用于均匀网格，当x,y,z方向的网格大小不一样的时候，这个网格积分得进行修改
        grid_area=self.grid.grid_spacing**2
        TE_fractions = []
        #公式计算
        for i, (Ex, Ey, Ez) in enumerate(zip(Ex_list, Ey_list, Ez_list)):
            # 计算 |E_x|^2, |E_y|^2, |E_z|^2
            Ex2 = np.abs(Ex)**2
            Ey2 = np.abs(Ey)**2
            Ez2 = np.abs(Ez)**2
            if axis == 'x':
               numerator = np.sum(Ey2) * grid_area#分子
               denominator=np.sum(Ey2 + Ez2) * grid_area#分母
            elif axis == 'y':
               numerator = np.sum(Ex2 ) * grid_area
               denominator=np.sum(Ex2 + Ez2) * grid_area
            elif axis == 'z':
               numerator = np.sum(Ex2 ) * grid_area
               denominator=np.sum(Ex2 + Ey2) * grid_area
            TE_fraction = numerator / denominator if denominator != 0 else 0
            # TE_fraction_percentage = round(TE_fraction * 100)  # 转为百分比并四舍五入
            TE_fractions.append(TE_fraction)
            # print(f"Mode {i + 1}: TE_fraction = {TE_fraction}")
            # 打印当前模式的 TE_fraction 百分比
            # print(f"Mode {i + 1}: TE_fraction = {TE_fraction_percentage}%")

        return TE_fractions





        #pass
        #
        # f = [0] * self.neigs
        # for i in range(self.neigs):
        #     f[i] = self.Ey_fields[i].real / self.Ex_fields[i].real
        #     plt.figure()
        #     plt.pcolor(self.x, self.y, self.n[:, :, 0], cmap=cm.Blues_r)
        #     plt.clim([1, np.amax(self.n)])
        #
        #     plot_matrix = np.transpose(f[i].real)
        #     levels = np.linspace(np.min(plot_matrix), np.max(plot_matrix), n_levels + 2)
        #     plt.pcolor(self.x, self.y, plot_matrix, cmap=cm.jet)
        #
        #     plt.savefig(fname='%s\\%s%f.png' % (self.filepath, 'EyEz', self.effective_index[i]))
        #     # plt.show()
        #     plt.close()


    def sweep(self,
              steps: int = 5,
              lams: list = []):
        # 在[lams[0], lams[1]]范围内计算steps个点, lam单位为um
        lams = np.linspace(lams[0], lams[1], steps)

        # phisol包在这里使用了一个函数来猜测扫描区间内折射率随波长的变化，但由于我们已经有材料库，所以应该用材料库的数据来估算。
        # TODO：这段代码暂时没用，有时间完成它
        # A = 2.17954368571
        # B = np.log(2.17954368571 / 1.75292972992) / 0.7
        # self.n_guess = A * np.exp(- B * (self.lam - 0.3))
        # 暂时用下式估算（只是测试代码是否可用，在物理上没有意义！）

        pass
        # n = np.zeros((steps, self.n.shape[0], self.n.shape[1], self.n.shape[2]))
        # for i in range(steps):
        #     n[i] = self.n
        #     env_index = np.zeros((self.n.shape[0], self.n.shape[1], self.n.shape[2]))
        #     env_index += np.sqrt(np.amax(self.grid.inverse_permittivity) * np.amax(self.grid.inverse_permeability))
        #     # mask.shape=(self.n.shape[0], self.n.shape[1], self.n.shape[2]), 其元素为True或False
        #     mask = n[i] != env_index
        #     # 若折射率!=环境折射率，则减去波长/10（仅为测试）
        #     n[i][mask] -= lams[i] / 10
        #
        # # 有必要计算多个模式吗？
        # neigs = 5
        #
        # # 由self.Ex_fields还原calculate_mode函数中的Ex
        # Ex = np.array([np.ravel(E_field) for E_field in self.Ex_fields])
        # Ex = np.reshape(Ex, (self.neigs, self.Ex_fields[0].shape[0] * self.Ex_fields[0].shape[1]))
        # Ey = np.array([np.ravel(E_field) for E_field in self.Ey_fields])
        # Ey = np.reshape(Ex, (self.neigs, self.Ey_fields[0].shape[0] * self.Ey_fields[0].shape[1]))
        #
        # # E_in将作为E_trial输入到函数ps.solve.solve中，其作用是作为迭代的起始向量，它是(self.neigs, self.grid.xlength*self.grid.ylength)的ndarray
        # E_in = np.concatenate((Ex[0], Ey[0]))
        #
        # # Now we have a go sweeping
        # beta_out = []
        # Ey_plot = []
        # Ex_plot = []
        #
        # # n_trial是一个规格为（steps)的一维矩阵，其值为材料在对应波长的折射率
        # # 这句代码仅作测试，没有物理意义！
        # n_trial = np.amax(self.n) - lams / 10
        #
        # # TODO: Fix complex casting warning （这是phisol包原作者留下的TODO，看不懂什么意思）
        # for i in range(steps):
        #     k = 2. * np.pi / lams[i]
        #     P, _ = ps.eigen_build(k, n[i], self.grid.grid_spacing * 1e6, self.grid.grid_spacing * 1e6)
        #
        #     # TODO: Fix complex casting warning
        #     # 为什么要计算neigs个模式
        #     beta, Ex, Ey = ps.solve.solve(P,
        #                                   2. * n_trial[i] * np.pi / lams[i],
        #                                   E_trial=E_in,
        #                                   neigs=neigs)
        #
        #     Ey_plot.append(
        #         [np.reshape(E_vec, (self.Ex_fields[0].shape[0], self.Ex_fields[0].shape[1])) for E_vec in Ey])
        #     Ex_plot.append(
        #         [np.reshape(E_vec, (self.Ex_fields[0].shape[0], self.Ex_fields[0].shape[1])) for E_vec in Ex])
        #     beta_out.append(beta)
        #
        # index = 0  # Select starting mode
        #
        # # Ex_plot的形状：[5,10,200,50] 指steps, neigs, x, y
        # # Initialise sweep trace arrays
        # beta_trace = [beta_out[0][index]]
        # Eyplottrace = [Ey_plot[0][index]]
        # Explottrace = [Ex_plot[0][index]]
        #
        # E_trace = []  # New reordering method. WIP
        #
        # # Plot selected mode for testing
        # # plt.figure()
        # # xend = np.size(x)
        # # yend = np.size(y)
        # # plt.pcolor(x, y, np.transpose(Eyplottrace[0].real), cmap=cm.jet)
        # # plt.title("Initial selected mode")
        # # plt.show()
        #
        # # Do sweep
        # indices = []  # Create an array to log the original position of the fundamental (just used for debugging)
        # for i in range(steps - 1):
        #     # Takes product of all modes with all next modes the largest value should be the same mode!
        #     # 使用了 numpy.einsum() 函数来计算两个电场 Ey_plot[i] 和 Ey_plot[i+1] 的张量积
        #     prod_next = abs(np.einsum('kij, lij', Ey_plot[i], Ey_plot[i + 1]))
        #
        #     # 将当前时刻的电场矩阵（Ey_plot[i]）与下一时刻的电场矩阵的内积（prod_next）进行乘积运算（np.einsum('kij, kl', Ey_plot[i], prod_next)），
        #     # 并将结果添加到电场轨迹列表 E_trace 中
        #     E_trace.append(np.einsum('kij, kl', Ey_plot[i], prod_next))  # New reordering method. WIP
        #
        #     # 找到一个多维数组prod_next中指定行index中的最大值，然后返回这个最大值在该行的列索引
        #     # 我估计这是在找不同波长下的基模，假如想看其他模式的扫描图，就得更改代码
        #     # TODO:完成它
        #     index = np.argmax(prod_next[index, :])
        #     indices.append(index)  # Append the index, for debugging
        #
        #     beta_trace.append(beta_out[i + 1][index])
        #     Eyplottrace.append(Ey_plot[i + 1][index])
        #     Explottrace.append(Ex_plot[i + 1][index])
        #
        # print(indices)  # Show indices, for debugging
        #
        # # Now we can plot the dispersion and e field
        # plt.figure()
        # plt.plot(lams, np.real(beta_trace))
        # plt.xlabel('$/lambda / /mu m$')
        # plt.ylabel(r'$/beta [ /mu m^{-1} ]$')
        # plt.title("Structure dispersion")
        # plt.savefig(fname='%s\\%s.png' % (self.filepath, 'wavelength_beta'))
        # plt.close()
        #
        # # Finally plot the mode at some sweep position 'some_random_point', for testing
        # # plt.figure()
        # # some_random_point = -1  # Last value in sweep
        # # xend = np.size(x)
        # # yend = np.size(y)
        # # plt.pcolor(x, y, np.transpose(Eyplottrace[some_random_point].real), cmap=cm.inferno)
        # # plt.title("Selected mode")
        # plt.show()
    import numpy as np


