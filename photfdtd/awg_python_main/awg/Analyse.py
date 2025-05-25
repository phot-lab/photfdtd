from tabulate import tabulate
import numpy as np
from .Simulate import Simulate
from scipy.signal import find_peaks

class Analyse:
    """
    Perform analysis on output spectrum.

    参数:
    - lambda_c: 设计的中心波长
    - channel_spacing: 通道间隔
    """

    def __init__(self, results):
        lmbda = results.wavelength  # 波长数据
        T = results.transmission    # 透射率数据

        TdB = 10 * np.log10(T)      # 转换为 dB 单位
        num_channels = np.shape(T)[1]#获取通道数目
        center_channel = int(num_channels / 2) - 1 if num_channels % 2 == 0 else int(num_channels / 2)#中心通道的索引

        # 插入损耗（Insertion Loss）
        self.IL = abs(np.max(TdB[:, center_channel]))

        # 归一化中心通道的透射谱，减去插入损耗，最大值为 0dB
        t0 = TdB[:, center_channel] - self.IL
        ic = np.argmax(t0)#找到中心通道透射最大值（= 0 dB）对应的索引

        # 10dB 带宽，在中心通道中，从最大值往前/后找小于 -10 dB 和 -3 dB 的位置，计算带宽。
        ia10 = np.argwhere(t0[:ic+1] < -10)[-1][0]
        ib10 = ic + np.argwhere(t0[ic:] < -10)[1][0]
        self.BW10 = (lmbda[ib10] - lmbda[ia10]) * 1e3  # 单位 nm

        # 3dB 带宽
        ia3 = np.argwhere(t0[:ic+1] < -3)[-1][0]
        ib3 = ic + np.argwhere(t0[ic:] < -3)[1][0]
        self.BW3 = (lmbda[ib3] - lmbda[ia3]) * 1e3      # 单位 nm
        self.center_wavelength = (lmbda[ia3] + lmbda[ib3]) / 2  # 单位 μm

        # 非均匀性、通道间距、串扰初始化
        self.NU = 0
        self.CS = 0
        self.XT = 0
        self.XTn = -100

        # 非均匀性：最左通道与中心通道插入损耗差值
        if num_channels > 1:
            self.NU = abs(np.max(TdB[:, 0])) - self.IL#最左侧通道的最大传输值与中心通道插入损耗的差值

            # 相邻串扰：中心通道 ±1 通道，在其 3dB 带宽范围内的最大透射值，然后再减去中心通道的最大透射值（即插入损耗 IL）得到串扰大小（单位 dB，通常为负值）
            if num_channels < 3:
                if center_channel > 1:
                    self.XT = np.max(TdB[ia3:ib3, center_channel - 1])
                else:
                    self.XT = np.max(TdB[ia3:ib3, center_channel + 1])
            else:
                xt1 = np.max(TdB[ia3:ib3, center_channel - 1])
                xt2 = np.max(TdB[ia3:ib3, center_channel + 1])
                self.XT = max(xt1, xt2)
            self.XT -= self.IL

        # 非相邻串扰（排除中心通道和相邻通道）
        for i in range(num_channels):
            if i != center_channel:
                xt = np.max(TdB[ia3:ib3+1, i])
                self.XTn = max(self.XTn, xt)
        self.XTn -= self.IL

        # 通道间距（Channel Spacing）
        if num_channels < 3:
            if center_channel > 1:
                ia = np.argmax(TdB[:, center_channel - 1])
                self.CS = 1e3 * abs(lmbda[ia] - lmbda[ic])
            else:
                ia = np.argmax(TdB[:, center_channel + 1])
                self.CS = 1e3 * abs(lmbda[ia] - lmbda[ic])
        else:
            ia = np.argmax(TdB[:, center_channel - 1])
            ib = np.argmax(TdB[:, center_channel + 1])
            sp1 = abs(lmbda[ia] - lmbda[ic])
            sp2 = abs(lmbda[ib] - lmbda[ic])
            self.CS = max(sp1, sp2) * 1e3

        # 汇总指标值
        self.Value = [
            self.IL,
            self.NU,
            self.center_wavelength * 1e3,
            self.CS,
            self.BW3,
            self.BW10,
            self.XT,
            self.XTn,
        ]

    def __str__(self):
        return tabulate([
            ['Insertion loss [dB]', self.IL],
            ['Loss non-uniformity [dB]', self.NU],
            ['Center wavelength [nm]', self.center_wavelength * 1e3],
            ['Channel spacing [nm]', self.CS],
            ['3dB bandwidth [nm]', self.BW3],
            ['10dB bandwidth [nm]', self.BW10],
            ['Adjacent crosstalk level [dB]', self.XT],
            ['Non-adjacent crosstalk level [dB]', self.XTn],
        ], headers=['Metric', 'Value'])
