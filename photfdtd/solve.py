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
            filepath=grid.folder
        self.grid = grid._grid
        self.geometry = np.sqrt(1 / self.grid.inverse_permittivity)
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

    def plot(self):
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
        plt.savefig(fname='%s\\%s_%s=%d.png' % (self.filepath, 'index', self.axis, self.index))

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
        x_thickness_low, x_thickness_high, y_thickness_low, y_thickness_high = \
            self.grid._handle_distance(x_thickness_low), self.grid._handle_distance(x_thickness_high), \
            self.grid._handle_distance(y_thickness_low), self.grid._handle_distance(y_thickness_high),
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
        for i in range(len(self.beta)):
            # Discard dispersion modes丢掉耗散模
            # print(abs(self.beta[i].imag * self.lam / (2 * np.pi)))
            if abs(self.beta[i].imag * self.lam / (2 * np.pi)) > 1e-5:
                flag_deleted.append(i)
                neigs -= 1
        self.beta, Ex_field, Ey_field = np.delete(self.beta, flag_deleted), \
                                        np.delete(Ex_field, flag_deleted, 0), \
                                        np.delete(Ey_field, flag_deleted, 0)
        print("%i dispersion modes are discarded" % len(flag_deleted))

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

        dic = {}

        # 似乎原代码中Ex, Ey和Hx, Hy弄反了，所以我在这里调换了一下
        dic["Ex"] = Ey
        dic["Ey"] = Ex
        dic["Ez"] = Ez
        dic["Hx"] = Hy
        dic["Hy"] = Hx
        dic["Hz"] = Hz
        dic["number_of_modes"] = neigs
        dic["effective_index"] = self.effective_index
        dic["axis"] = self.axis
        dic["grid_spacing"] = self.grid.grid_spacing
        dic["lam"] = lam
        return dic

    @staticmethod
    def draw_mode(filepath,
                  data: list = None,
                  content: str = "amplitude"
                  ) -> None:
        '''
        绘制模式，保存图片与相应的有效折射率
        :param neigs: 绘制模式数
        :param component: ey: 绘制Ey ex: 绘制Ex # TODO: Ez与磁场？
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

                plt.title('%s_of_%s, neff=%s' % (content, j, str(effective_index[i])))
                # 保存图片
                plt.savefig(fname='%s\\%s%d_%s_%s.png' % (filepath, 'mode', i + 1, content, j))
                plt.close()

        # Draw E/H intensity
        for i in range(data["number_of_modes"]):
            if axis == "x":
                E_intensity = data["Ey"][i].real ** 2 + data["Ez"][i].real ** 2
                H_intensity = data["Hy"][i].real ** 2 + data["Hz"][i].real ** 2
            if axis == "y":
                E_intensity = data["Ex"][i].real ** 2 + data["Ez"][i].real ** 2
                H_intensity = data["Hx"][i].real ** 2 + data["Hz"][i].real ** 2
            if axis == "z":
                E_intensity = data["Ex"][i].real ** 2 + data["Ey"][i].real ** 2
                H_intensity = data["Hx"][i].real ** 2 + data["Hy"][i].real ** 2
            E_intensity = np.transpose(E_intensity)
            H_intensity = np.transpose(H_intensity)
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
            plt.title('E_intensity, neff=%s' % (str(effective_index[i])))
            # 保存图片
            plt.savefig(fname='%s\\%s%d_E_intensity.png' % (filepath, 'mode', i + 1))
            plt.close()

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
            plt.title('H_intensity, neff=%s' % (str(effective_index[i])))
            # 保存图片
            plt.savefig(fname='%s\\%s%d_H_intensity.png' % (filepath, 'mode', i + 1))
            plt.close()

        # Draw neff plot
        # plt.plot(np.linspace(1, len(effective_index), len(effective_index)), effective_index.real, label='Line',
        #          marker="o")
        # plt.title('neff plot')
        # plt.xticks(np.arange(1, len(effective_index), 1))
        # plt.xlabel('mode')
        # plt.savefig(fname='%s\\%s.png' % (filepath, 'neff_plot'))
        # plt.close()

        # Draw loss plot
        loss = -20 * np.log10(np.e ** (-2 * np.pi * effective_index.imag / lam))
        # plt.plot(np.linspace(1, len(effective_index), len(effective_index)), loss, label='Line',
        #          marker="o")
        # plt.title('loss plot')
        # plt.xticks(np.arange(1, len(effective_index), 1))
        # plt.xlabel('mode')
        # plt.ylabel('dB/m')
        # plt.savefig(fname='%s\\%s.png' % (filepath, 'loss_plot'))
        # plt.close()

    @staticmethod
    def save_mode(folder, dic):
        # 保存计算的模式
        np.savez(path.join(folder, "saved_modes"), **dic)

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
                             n_levels: int = 6,
                             ) -> None:
        """
        绘制不同模式的Ey与Ex的实部之比，并保存
        # TODO: 在lumerical中，TE fracttion 来自全区域电场的平方积分之比，得到的是一个数，并不是这种算法。是否需要改正？
        :param filepath: 保存图片路径
        :return: None
        """

        pass
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
