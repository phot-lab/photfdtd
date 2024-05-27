import numpy as np
from scipy.signal import find_peaks
from matplotlib import pyplot as plt


class Analyse:
    '''处理监视器数据：计算坡印廷矢量、计算功率、计算透过率'''

    def __init__(self, E, H, grid_spacing):
        """
        :param E: 电场。E、H为监视器数据，为三维矩阵（对应线监视器 [timestep, couple_length, 3]）或五维矩阵（对应矩形监视器[timestep, xlength, ylength,
        zlength, 3]）
        :param H: 磁场
        :param grid_spacing: 空间步长
        :param direction: 方向(x, y, z)
        self.P_positive: 正向的瞬时功率
        self.P_positive: 负向的瞬时功率
        """
        # TODO: 还是不能确定是否是标准单位
        self.grid_spacing = grid_spacing
        # fdtd中的E与真实的E的关系是前者=后者 * sqrt(const.eps0), 而H与真实的H的关系是前者=后者 * sqrt(const.mu0)
        # 见https://www.photonics.intec.ugent.be/download/phd_259.pdf 4.1.2-4.1.6 （python fdtd原作者的毕业论文）
        # 因此 坡印廷矢量P = c * E x H
        # 坡印廷矢量，单位W/m^2(矩形监视器) 或W/m(线监视器)
        self.P = 299792458.0 * np.cross(E, np.conj(H), axis=-1)

        print(self.P.shape[1])
        print(self.P.shape)

        # 分别保存正向与负向的P
        self.P_positive = self.P[self.P > 0]
        self.P_negative = self.P[self.P < 0]

        # 使用布尔索引筛选出所有正的元素
        self.P_positive = self.P > 0
        self.P_negative = self.P < 0

        self.P_positive = np.where(self.P_positive, self.P, 0)
        self.P_negative = np.where(self.P_negative, self.P, 0)

        # 字典Powr保存三个x,y,z三个方向上的瞬时频率
        self.Power = {}
        for i in range(3):
            if self.P.ndim == 3:
                self.a = self.P_positive[:, :, i]
                self.b = self.P_negative[:, :, i]

                self.Power["power_positive_%s" % chr(i + 120)] = np.sum(self.a, axis=1) / 2 * \
                                                            self.P.shape[1] * self.grid_spacing
                self.Power["power_negative_%s" % chr(i + 120)] = np.sum(self.b, axis=1) / 2 * \
                                                            self.P.shape[1] * self.grid_spacing

            elif self.P.ndim == 5:
                self.a = self.P_positive[:, :, :, i]
                self.b = self.P_positive[:, :, :, i]

                self.Power["power_positive_%s" % chr(i + 120)] = np.sum(self.a, axis=(1, 2, 3)) / 2 * self.P.shape[1] * \
                                                            self.P.shape[2] * self.P.shape[3] * (self.grid_spacing ** 2)
                self.Power["power_negative_%s" % chr(i + 120)] = np.sum(self.b, axis=(1, 2, 3)) / 2 * self.P.shape[1] * \
                                                            self.P.shape[2] * self.P.shape[3] * (self.grid_spacing ** 2)
            else:
                raise ValueError("Invalid shape of E or H!")

        del self.a, self.b

        # 由坡印廷矢量得到功率Power
        # if self.P.ndim == 4:
        #     self.P_positive = np.sum(self.P_positive, axis=(1, 2, 3)) / 2 * self.P.shape[1] * self.P.shape[2] \
        #                           * self.P.shape[3] * (self.grid_spacing ** 2)
        #     self.P_negative = np.sum(self.P_negative, axis=(1, 2, 3)) / 2 * self.P.shape[1] * self.P.shape[2] \
        #                           * self.P.shape[3] * (self.grid_spacing ** 2)
        # elif self.P.ndim == 2:
        #     self.P_positive = np.sum(self.P_positive, axis=1) / 2 * self.P.shape[1] * self.grid_spacing
        #     self.P_negative = np.sum(self.P_negative, axis=1) / 2 * self.P.shape[1] * self.grid_spacing
        # else:
        #     raise ValueError("Invalid shape of E or H!")

        # self.realE = conversions.simE_to_worldE(E)
        # self.realH = conversions.simH_to_worldH(H)

    def plot(self):

        # pass
        #TODO: 完成它
        t = np.linspace(0, len(self.Power["power_positive_x"]), len(self.Power["power_positive_x"]))
        plt.plot(t, self.Power["power_positive_x"], label='Px+')
        plt.plot(t, self.Power["power_negative_x"], label='Px-')
        plt.plot(t, self.Power["power_positive_y"], label='Py+')
        plt.plot(t, self.Power["power_negative_y"], label='Py-')
        plt.plot(t, self.Power["power_positive_z"], label='Pz+')
        plt.plot(t, self.Power["power_negative_z"], label='Pz-')  # 绘制曲线，添加标签
        plt.title('Power Plot')  # 添加标题
        plt.xlabel('t')  # 添加x轴标签
        plt.ylabel('y')  # 添加y轴标签
        plt.legend()  # 添加图例
        plt.grid()  # 添加网格线
        plt.show()  # 显示图表

    def caculate_P(self):
        """
        计算坡印廷矢量 P = E x H
        self.P为三维或五维矩阵, shape与E和H一致
        """
        pass
        # (lumerical官网上是E叉乘H的共轭，而meep是E的共轭叉乘H...)
        # self.P = np.cross(self.E, self.H, axis=-1)

    def calculate_Power(self):

        """由坡印廷矢量P计算功率power
        根据lumerical官网，功率=监视器表面的坡印廷矢量的实部的积分/2 （需不需要区分方向？）"""

        # TODO: 换算成标准单位
        # Power = np.zeros(self.P.shape[0])
        # axis参数指定在哪些维度上进行求和，这里指定为后四个维度, 或后两个
        pass
        # half_max_Power = np.max(self.Power) / 2
        # 调用scipy包计算波峰数，保存在peaks中。peaks.shape=[波峰数]，其元素为波峰的索引 （有没有办法不调用scipy包？）
        # 只有波峰大于half_max_Power才会被计算
        # peaks, _ = find_peaks(self.Power, height=half_max_Power)
        # peaks, _ = find_peaks(self.Power)
        # result = 0
        # 计算总功率，单纯的把所有功率相加（这样有问题吗？）
        # for i in range(self.P.shape[0]):
        #     result += self.Power[i]

        # self.power保存总功率除以波峰数量
        # 若RuntimeWarning: invalid value encountered in double_scalars
        #  self.Power = result / len(peaks)， 说明监视器保存的数据为0
        # if len(peaks) == 0:
        #     print("监视器未接收到任何数据，延长模拟时间或检查光路设置")
        # else:
        #     self.Power = result / len(peaks)


if __name__ == "__main__":
    # 读取监视器保存的E、H参数
    file_path = "D:/下载内容/photfdtd-main/tests/fdtd_output/fdtd_output_2023-4-3-15-27-58 (" \
                "test0403)/detector_readings.npz "
    p = np.load(file_path, allow_pickle=True)
    print(p.files)

    # 光源E，H
    ds_E, ds_H = p['detector_source (E)'], p['detector_source (H)']
    # 光路末端E，H
    d1_E = p['detector_bottom (E)']
    d1_H = p['detector_bottom (H)']

    calculate_source = Analyse(ds_E, ds_H)
    calculate_detector = Analyse(d1_E, d1_H)

    calculate_source.caculate_P()
    calculate_detector.caculate_P()

    calculate_source.calculate_Power()
    calculate_detector.calculate_Power()

    T = calculate_detector.Power / calculate_source.Power
    print('T = %f' % T)
