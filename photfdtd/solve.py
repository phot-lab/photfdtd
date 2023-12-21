# import utils
from photfdtd import Waveguide, Grid
import photfdtd.philsol as ps
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
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
                 ):
        '''
        23.03.18
        本函数除了作为__init__函数，其主要功能是将fdtd.grid变量及其内部保存的waveguide映射到矩阵self.geometry中。
        self.geometry是一个四维矩阵 [x,y,z,3]，这是因为对于各向异性材料，它们在x，y，z三个方向上折射率不同，所以需要四维才能表现。
        但暂时还不能编辑各向异性材料
        :param grid: fdtd.grid
        '''
        self.grid = grid._grid
        geo = np.sqrt(1 / self.grid.inverse_permittivity)
        for i in range(len(self.grid.objects)):
            geo[self.grid.objects[i].x.start:self.grid.objects[i].x.stop,
            self.grid.objects[i].y.start:self.grid.objects[i].y.stop,
            self.grid.objects[i].z.start:self.grid.objects[i].z.stop] = np.sqrt(self.grid.objects[i].permittivity)
        self.geometry = geo

    def plot(self,
             axis: str = 'x',
             index: int = 0,
             filepath: str = ''
             ):
        """
        绘制截面图。
        :param: axis: 哪个轴的截面
        :param: index: 轴上哪点
        :param: filepath: 保存图片的文件夹
        :return: None
        # 23.4.17: 更改了保存图片的名称
        """
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
            raise RuntimeError('axis should be x, y or z! ')

        self.x = np.linspace(1, np.size(self.n, 0), np.size(self.n, 0))
        self.y = np.linspace(1, np.size(self.n, 1), np.size(self.n, 1))

        # 这里计划日后加入判断是否是各向异性材料
        if True:
            # 做转置，这样在显示时x就会被放在水平轴上
            # FIXME: 这确定没错？
            self.n = np.transpose(self.n, [1, 0, 2])
        else:
            pass

        # 绘制
        plt.pcolor(self.n[:, :, 0], cmap=cm.jet)
        plt.clim([1.0, np.amax(self.n)])
        plt.colorbar()
        # 保存图片
        plt.savefig(fname='%s\\%s_%s=%d.png' % (self.filepath, 'index', axis, index))

        # plt.show()
        plt.clf()
        plt.close()

    def calculate_mode(self,
                       lam: float = 1550e-9,
                       neff: float = None,
                       neigs: int = 1,
                       x_boundary_low=None, y_boundary_low=None, x_thickness_low=0, y_thickness_low=0,
                       x_boundary_high=None, y_boundary_high=None, x_thickness_high=0, y_thickness_high=0
                       ):
        """
        调用phisol包，计算模式并绘制模式。
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
        # NOTE: fdtd的单位是m，而philsol的单位是um
        if neff == None:
            neff = np.max(self.n)
        self.lam = lam * 10 ** 6
        self.k = 2 * np.pi / self.lam

        # 调用phisol包，计算模式
        P, matrices = ps.eigen_build(self.k, self.n, self.grid.grid_spacing * 1e6, self.grid.grid_spacing * 1e6,
                                     x_boundary_low=x_boundary_low, y_boundary_low=y_boundary_low,
                                     x_thickness_low=x_thickness_low,
                                     y_thickness_low=y_thickness_low, x_boundary_high=x_boundary_high,
                                     y_boundary_high=y_boundary_high, x_thickness_high=x_thickness_high,
                                     y_thickness_high=y_thickness_high)
        beta_in = 2. * np.pi * neff / self.lam
        self.beta, Ex_field, Ey_field = ps.solve.solve(P, beta_in, neigs=neigs)
        del P  # 并不必要，只是为了节省内存
        self.effective_index = self.beta * self.lam / (2 * np.pi)
        print("neff=", self.effective_index)

        if self.axis == 'x':
            Ex = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hx = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hy = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hz = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

            for i in range(neigs):
                Ex[i], Hy[i], Hz[i], Hx[i] = ps.construct.extra_feilds(k0=self.k, beta=self.beta[i],
                                                                       Ex=Ex_field[i], Ey=Ey_field[i],
                                                                       matrices=matrices)
            Ex = [np.reshape(E_vec, (self.grid.Ny, self.grid.Nz)) for E_vec in Ex]
            Hx = [np.reshape(E_vec, (self.grid.Ny, self.grid.Nz)) for E_vec in Hx]
            Hy = [np.reshape(E_vec, (self.grid.Ny, self.grid.Nz)) for E_vec in Hy]
            Hz = [np.reshape(E_vec, (self.grid.Ny, self.grid.Nz)) for E_vec in Hz]


        elif self.axis == 'y':

            Ey = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hx = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hy = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hz = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

            for i in range(neigs):
                Ey[i], Hx[i], Hz[i], Hy[i] = ps.construct.extra_feilds(k0=self.k, beta=self.beta[i],
                                                                       Ex=Ex_field[i], Ey=Ey_field[i],
                                                                       matrices=matrices)

            Ey = [np.reshape(E_vec, (self.grid.Nx, self.grid.Nz)) for E_vec in Ey_field]
            Hx = [np.reshape(E_vec, (self.grid.Nx, self.grid.Nz)) for E_vec in Hx]
            Hy = [np.reshape(E_vec, (self.grid.Nx, self.grid.Nz)) for E_vec in Hy]
            Hz = [np.reshape(E_vec, (self.grid.Nx, self.grid.Nz)) for E_vec in Hz]


        elif self.axis == 'z':

            Ez = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hx = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hy = np.empty((neigs, Ex_field.shape[1]), dtype=complex)
            Hz = np.empty((neigs, Ex_field.shape[1]), dtype=complex)

            for i in range(neigs):
                Ez[i], Hx[i], Hy[i], Hz[i] = ps.construct.extra_feilds(k0=self.k, beta=self.beta[i], Ex=Ex_field[i],
                                                                       Ey=Ey_field[i], matrices=matrices)
            Ez = [np.reshape(E_vec, (self.grid.Nx, self.grid.Ny)) for E_vec in Ez]
            Hx = [np.reshape(E_vec, (self.grid.Nx, self.grid.Ny)) for E_vec in Hx]
            Hy = [np.reshape(E_vec, (self.grid.Nx, self.grid.Ny)) for E_vec in Hy]
            Hz = [np.reshape(E_vec, (self.grid.Nx, self.grid.Ny)) for E_vec in Hz]

        dic = {}

        if not "Ex" in vars():
            Ex = Ex_field
            Ex = [np.reshape(E_vec, (self.grid.Nx, self.grid.Ny)) for E_vec in Ex]

        if not "Ey" in vars():
            Ey = Ey_field
            Ey = [np.reshape(E_vec, (self.grid.Nx, self.grid.Ny)) for E_vec in Ey]

        del Ex_field, Ey_field, matrices  # 节省内存

        # 似乎原代码中Ex, Ey和Hx, Hy弄反了，所以我在这里调换了一下
        dic["Ex"] = Ey
        del Ey  # 节省内存
        dic["Ey"] = Ex
        del Ex
        dic["Ez"] = Ez
        del Ez
        dic["Hx"] = Hy
        del Hy
        dic["Hy"] = Hx
        del Hx
        dic["Hz"] = Hz
        del Hz
        dic["number_of_modes"] = neigs
        dic["effective_index"] = self.effective_index
        dic["axis"] = self.axis

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
        # 绘制模式图
        x = np.linspace(1, np.size(data["Ex"][0], 0), np.size(data["Ex"][0], 0))
        y = np.linspace(1, np.size(data["Ex"][0], 1), np.size(data["Ex"][0], 1))
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

                plt.pcolor(x, y, plot_matrix, cmap=cm.jet)
                plt.clim([np.amin(plot_matrix), np.amax(plot_matrix)])
                plt.colorbar()
                if axis == "x":
                    plt.xlabel('Y')
                    plt.ylabel('Z')
                elif axis == "y":
                    plt.xlabel('X')
                    plt.ylabel('Z')
                elif axis == "z":
                    plt.xlabel('X')
                    plt.ylabel('Y')

                plt.title('%s_of_%s, neff=%f' % (content, j, effective_index[i]))
                # 保存图片
                plt.savefig(fname='%s\\%s%d_%s_%s.png' % (filepath, 'mode', i + 1, content, j))
                plt.close()

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
        del readings
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
        f = [0] * self.neigs
        for i in range(self.neigs):
            f[i] = self.Ey_fields[i].real / self.Ex_fields[i].real
            plt.figure()
            plt.pcolor(self.x, self.y, self.n[:, :, 0], cmap=cm.Blues_r)
            plt.clim([1, np.amax(self.n)])

            plot_matrix = np.transpose(f[i].real)
            levels = np.linspace(np.min(plot_matrix), np.max(plot_matrix), n_levels + 2)
            plt.pcolor(self.x, self.y, plot_matrix, cmap=cm.jet)

            plt.savefig(fname='%s\\%s%f.png' % (self.filepath, 'EyEz', self.effective_index[i]))
            # plt.show()
            plt.close()

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
        n = np.zeros((steps, self.n.shape[0], self.n.shape[1], self.n.shape[2]))
        for i in range(steps):
            n[i] = self.n
            env_index = np.zeros((self.n.shape[0], self.n.shape[1], self.n.shape[2]))
            env_index += np.sqrt(np.amax(self.grid.inverse_permittivity) * np.amax(self.grid.inverse_permeability))
            # mask.shape=(self.n.shape[0], self.n.shape[1], self.n.shape[2]), 其元素为True或False
            mask = n[i] != env_index
            # 若折射率!=环境折射率，则减去波长/10（仅为测试）
            n[i][mask] -= lams[i] / 10

        # 有必要计算多个模式吗？
        neigs = 5

        # 由self.Ex_fields还原calculate_mode函数中的Ex
        Ex = np.array([np.ravel(E_field) for E_field in self.Ex_fields])
        Ex = np.reshape(Ex, (self.neigs, self.Ex_fields[0].shape[0] * self.Ex_fields[0].shape[1]))
        Ey = np.array([np.ravel(E_field) for E_field in self.Ey_fields])
        Ey = np.reshape(Ex, (self.neigs, self.Ey_fields[0].shape[0] * self.Ey_fields[0].shape[1]))

        # E_in将作为E_trial输入到函数ps.solve.solve中，其作用是作为迭代的起始向量，它是(self.neigs, self.grid.xlength*self.grid.ylength)的ndarray
        E_in = np.concatenate((Ex[0], Ey[0]))

        # Now we have a go sweeping
        beta_out = []
        Ey_plot = []
        Ex_plot = []

        # n_trial是一个规格为（steps)的一维矩阵，其值为材料在对应波长的折射率
        # 这句代码仅作测试，没有物理意义！
        n_trial = np.amax(self.n) - lams / 10

        # TODO: Fix complex casting warning （这是phisol包原作者留下的TODO，看不懂什么意思）
        for i in range(steps):
            k = 2. * np.pi / lams[i]
            P, _ = ps.eigen_build(k, n[i], self.grid.grid_spacing * 1e6, self.grid.grid_spacing * 1e6)

            # TODO: Fix complex casting warning
            # 为什么要计算neigs个模式
            beta, Ex, Ey = ps.solve.solve(P,
                                          2. * n_trial[i] * np.pi / lams[i],
                                          E_trial=E_in,
                                          neigs=neigs)

            Ey_plot.append(
                [np.reshape(E_vec, (self.Ex_fields[0].shape[0], self.Ex_fields[0].shape[1])) for E_vec in Ey])
            Ex_plot.append(
                [np.reshape(E_vec, (self.Ex_fields[0].shape[0], self.Ex_fields[0].shape[1])) for E_vec in Ex])
            beta_out.append(beta)

        index = 0  # Select starting mode

        # Ex_plot的形状：[5,10,200,50] 指steps, neigs, x, y
        # Initialise sweep trace arrays
        beta_trace = [beta_out[0][index]]
        Eyplottrace = [Ey_plot[0][index]]
        Explottrace = [Ex_plot[0][index]]

        E_trace = []  # New reordering method. WIP

        # Plot selected mode for testing
        # plt.figure()
        # xend = np.size(x)
        # yend = np.size(y)
        # plt.pcolor(x, y, np.transpose(Eyplottrace[0].real), cmap=cm.jet)
        # plt.title("Initial selected mode")
        # plt.show()

        # Do sweep
        indices = []  # Create an array to log the original position of the fundamental (just used for debugging)
        for i in range(steps - 1):
            # Takes product of all modes with all next modes the largest value should be the same mode!
            # 使用了 numpy.einsum() 函数来计算两个电场 Ey_plot[i] 和 Ey_plot[i+1] 的张量积
            prod_next = abs(np.einsum('kij, lij', Ey_plot[i], Ey_plot[i + 1]))

            # 将当前时刻的电场矩阵（Ey_plot[i]）与下一时刻的电场矩阵的内积（prod_next）进行乘积运算（np.einsum('kij, kl', Ey_plot[i], prod_next)），
            # 并将结果添加到电场轨迹列表 E_trace 中
            E_trace.append(np.einsum('kij, kl', Ey_plot[i], prod_next))  # New reordering method. WIP

            # 找到一个多维数组prod_next中指定行index中的最大值，然后返回这个最大值在该行的列索引
            # 我估计这是在找不同波长下的基模，假如想看其他模式的扫描图，就得更改代码
            # TODO:完成它
            index = np.argmax(prod_next[index, :])
            indices.append(index)  # Append the index, for debugging

            beta_trace.append(beta_out[i + 1][index])
            Eyplottrace.append(Ey_plot[i + 1][index])
            Explottrace.append(Ex_plot[i + 1][index])

        print(indices)  # Show indices, for debugging

        # Now we can plot the dispersion and e field
        plt.figure()
        plt.plot(lams, np.real(beta_trace))
        plt.xlabel('$/lambda / /mu m$')
        plt.ylabel(r'$/beta [ /mu m^{-1} ]$')
        plt.title("Structure dispersion")
        plt.savefig(fname='%s\\%s.png' % (self.filepath, 'wavelength_beta'))
        plt.close()

        # Finally plot the mode at some sweep position 'some_random_point', for testing
        # plt.figure()
        # some_random_point = -1  # Last value in sweep
        # xend = np.size(x)
        # yend = np.size(y)
        # plt.pcolor(x, y, np.transpose(Eyplottrace[some_random_point].real), cmap=cm.inferno)
        # plt.title("Selected mode")
        # plt.show()


if __name__ == "__main__":
    # 设置器件参数
    waveguide = Waveguide(
        xlength=100, ylength=20, zlength=10, x=50, y=20, z=10, width=10, refractive_index=3.47, name="Waveguide"
    )
    # # 新建一个 grid 对象
    # grid = Grid(grid_xlength=100, grid_ylength=40, grid_zlength=20, grid_spacing=11e-9, total_time=1)
    #
    # # 往 grid 里添加一个器件
    # grid.add_object(waveguide)
    #
    # # 创建solve对象
    # solve = Solve(grid=grid)
    #
    # # 绘制x=50截面
    # solve.plot(axis='x',
    #            index=50,
    #            filepath='D:/')
    #
    # # 计算这个截面处，波长1.55um，折射率3.47附近的10个模式
    # solve.calculate_mode(lam=1.55, neff=3.47, neigs=10)
    #
    # # 绘制计算的10个模式并保存，绘制时使用6个等高线
    # solve.draw_mode(neigs=10)
    #
    # # 计算各个模式的TEfraction，并保存图片
    # solve.calculate_TEfraction(n_levels=6)
    #
    # # 频率扫描，波长范围为[1.45um, 1.55um] 一共计算五个点
    # solve.sweep(steps=5,
    #             lams=[1.45, 1.55])
    #
    # # # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图（这里画了三张图）
    # # grid.savefig(filepath="WaveguideX.png", axis="x")
    # # grid.savefig(filepath="WaveguideY.png", axis="y")
    # # grid.savefig(filepath="WaveguideZ.png", axis="z")
