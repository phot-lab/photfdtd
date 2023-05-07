import numpy as np
from scipy.signal import find_peaks


class Analyse:
    """处理监视器数据：计算坡印廷矢量、计算功率、计算透过率"""

    def __init__(self, E, H):
        """
        :param E: 电场。E、H为监视器数据，为三维矩阵（对应线监视器 [timestep, couple_length, 3]）或五维矩阵（对应块监视器[timestep,xlength, ylength,
        zlength, 3]）
        :param H: 磁场
        """
        self.E = E
        self.H = H

    def caculate_P(self):
        """
        计算坡印廷矢量 P = E x H
        self.P为三维或五维矩阵, shape与E和H一致
        """
        # if len(self.E.shape) == 3:
        #     P = np.zeros([self.E.shape[0], self.E.shape[1], self.E.shape[2]])  # [timestep, length, 3]
        #     for i in range(self.E.shape[0]):
        #         for j in range(self.E.shape[1]):
        #             P[i, j, 0] = self.E[i, j, 1] * self.H[i, j, 2] - self.E[i, j, 2] * self.H[i, j, 1]
        #             P[i, j, 1] = self.E[i, j, 2] * self.H[i, j, 0] - self.E[i, j, 0] * self.H[i, j, 2]
        #             P[i, j, 2] = self.E[i, j, 0] * self.H[i, j, 1] - self.E[i, j, 1] * self.H[i, j, 0]

        # elif len(self.E.shape) == 5:
        #     P = np.zeros([self.E.shape[0], self.E.shape[1], self.E.shape[2], self.E.shape[3],
        #                  self.E.shape[4]])  # timestep,xlength, ylength,
        #     # zlength, 3]
        #     for i in range(self.E.shape[0]):
        #         for j in range(self.E.shape[1]):
        #             for k in range(self.E.shape[2]):
        #                 for l in range(self.E.shape[3]):
        #                     P[i, j, k, l, 0] = self.E[i, j, k, l, 1] * self.H[i, j, k, l, 2] - self.E[i, j, k, l, 2] * \
        #                                        self.H[i, j, k, l, 1]
        #                     P[i, j, k, l, 1] = self.E[i, j, k, l, 2] * self.H[i, j, k, l, 0] - self.E[i, j, k, l, 0] * \
        #                                        self.H[i, j, k, l, 2]
        #                     P[i, j, k, l, 2] = self.E[i, j, k, l, 0] * self.H[i, j, k, l, 1] - self.E[i, j, k, l, 1] * \
        #                                        self.H[i, j, k, l, 0]
        # else:
        #     raise RuntimeError("Invalid E/H form.")
        # 到底是P=E叉乘H还是叉乘H的共轭？
        self.P = np.cross(self.E, np.conj(self.H), axis=-1)

    def calculate_Power(self):
        """由坡印廷矢量P计算功率power
        根据lumerical官网，功率=监视器表面的坡印廷矢量的实部的积分/2 （需不需要区分方向？）"""

        # TODO: 换算成标准单位
        # Power = np.zeros(self.P.shape[0])
        # axis参数指定在哪些维度上进行求和，这里指定为后四个维度, 或后两个
        try:
            self.Power = np.sum(np.real(self.P), axis=(1, 2, 3, 4)) / 2
        except:
            self.Power = np.sum(np.real(self.P), axis=(1, 2)) / 2

        half_max_Power = np.max(self.Power) / 2
        # 调用scipy包计算波峰数，保存在peaks中。peaks.shape=[波峰数]，其元素为波峰的索引 （有没有办法不调用scipy包？）
        # 只有波峰大于half_max_Power才会被计算
        peaks, _ = find_peaks(self.Power, height=half_max_Power)

        result = 0
        # 计算总功率，单纯的把所有功率相加（这样有问题吗？）
        for i in range(self.P.shape[0]):
            result += self.Power[i]

        # self.power保存总功率除以波峰数量
        # 若RuntimeWarning: invalid value encountered in double_scalars
        #  self.Power = result / len(peaks)， 说明监视器保存的数据为0
        if len(peaks) == 0:
            print("监视器未接收到任何数据！")
        else:
            self.Power = result / len(peaks)


if __name__ == "__main__":
    # 读取监视器保存的E、H参数
    file_path = (
        "D:/下载内容/photfdtd-main/tests/fdtd_output/fdtd_output_2023-4-3-15-27-58 ("
        "test0403)/detector_readings.npz "
    )
    p = np.load(file_path, allow_pickle=True)
    print(p.files)

    # 光源E，H
    ds_E, ds_H = p["detector_source (E)"], p["detector_source (H)"]
    # 光路末端E，H
    d1_E = p["detector_bottom (E)"]
    d1_H = p["detector_bottom (H)"]

    calculate_source = Analyse(ds_E, ds_H)
    calculate_detector = Analyse(d1_E, d1_H)

    calculate_source.caculate_P()
    calculate_detector.caculate_P()

    calculate_source.calculate_Power()
    calculate_detector.calculate_Power()

    T = calculate_detector.Power / calculate_source.Power
    print("T = %f" % T)
