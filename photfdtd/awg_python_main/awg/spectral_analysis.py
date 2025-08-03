import numpy as np
from tabulate import tabulate


class Analyse:
    """
    Perform analysis on output spectrum.

    参数:
    - lambda_c: 设计的中心波长
    - channel_spacing: 通道间隔
    """

    def __init__(self, results,lambda_c, channel_spacing):
        lmbda = results.wavelength  # 光谱图里面的波长数据
        print("lmbda:",lmbda)
        T = abs(results.transmission)  # 光谱图里面的透射率数据

        TdB = 10 * np.log10(T)  # 转换为 dB 单位
        num_channels = np.shape(T)[1]  # 获取通道数目
        center_channel = int(num_channels / 2) - 1 if num_channels % 2 == 0 else int(num_channels / 2)  # 中心通道的索引
        # 各通道插入损耗（单位 dB）、3dB 带宽（单位 nm）、1dB 带宽（单位 nm）、中心波长（单位 μm）
        self.ILs = [np.max(TdB[:, i])for i in range(num_channels)]#插入损耗（单位 dB）,因为TdB进行了模操作，所以负数变成正数
        self.IL = max(self.ILs) # AWG的插入损耗（单位 dB），即所有通道中插入损耗最大的值（单位 dB）
        self.BW3s = []  # 各通道的 3dB 带宽（单位 nm）
        self.BW1s = []  # 各通道的 1dB 带宽（单位 nm）
        self.center_wavelengths = []  # 各通道的中心波长（单位 μm）
        for ch in range(num_channels):
            t = TdB[:, ch] - self.ILs[ch]  # 归一化每个通道传输曲线
            ic = np.argmax(t)  # 最大值索引（中心）
            # 3dB 带宽
            try:
                ia3 = np.argwhere(t[:ic + 1] < -3)[-1][0]
                ib3 = ic + np.argwhere(t[ic:] < -3)[1][0]
                bw3 = (lmbda[ib3] - lmbda[ia3]) * 1e3  # nm
            except IndexError:
                bw3 = 0
            self.BW3s.append(bw3)
            # 1dB 带宽
            try:
                ia1 = np.argwhere(t[:ic + 1] < -1)[-1][0]
                ib1 = ic + np.argwhere(t[ic:] < -1)[1][0]
                bw1 = (lmbda[ib1] - lmbda[ia1]) * 1e3  # nm
            except IndexError:
                bw1 = 0
            self.BW1s.append(bw1)
            # 中心波长
            try:
                cwl = (lmbda[ia3] + lmbda[ib3]) / 2  # um
            except:
                cwl = lmbda[ic]
            self.center_wavelengths.append(cwl)
        self.BW3 = min(self.BW3s)#带宽是指AWG各个通道带宽之最差情况,即最小值
        self.BW1 = min(self.BW1s)
        self.center_wavelength = self.center_wavelengths[center_channel] #中心通道的中心波长作为中心波长

        # 非均匀性、通道间距、串扰初始化
        self.NU = 0
        self.CS = 0
        self.AX = 0
        self.NX = -100

        #插入损耗非均匀性（Loss non-uniformity，NU）：所有通道插入损耗之间的最大差值,单位: dB
        self.NU =abs(max(self.ILs) - min(self.ILs))

        # 计算通道间隔(Channel spacing,CS),单位 nm
        center_wavelengths_nm = np.array(self.center_wavelengths) * 1e3  # um -> nm
        channel_spacings = np.diff(np.sort(center_wavelengths_nm))
        if len(channel_spacings) > 0:
            self.CS = np.mean(channel_spacings)
        else:
            self.CS = 0

        #相邻通道串扰：self.AX,非相邻通道串扰：self.NX
        self.AXs = []  # 每个通道的相邻串扰值（单位 dB）
        self.NXs = []  # 每个通道的非相邻串扰值（单位 dB）
        lambda_c_um = lambda_c  # 中心波长(单位 um)
        delta_um = channel_spacing  # 通道间隔(单位 um)
        passband_width = delta_um / 4  # 通带：以ITU-T 波长为中心,通常为ITU-T波长或者频率通道间隔的四分之一
        itu_centers = [lambda_c_um + (ch - center_channel) * delta_um for ch in range(num_channels)]## ITU中心波长列表
        for ch in range(num_channels):
            xt_left = xt_right = float('inf')
            lambda_ch = itu_centers[ch]
            wl_min = lambda_ch - passband_width / 2
            wl_max = lambda_ch + passband_width / 2
            indices = np.where((lmbda >= wl_min) & (lmbda <= wl_max))[0]
            if len(indices) == 0:
                self.AXs.append(0)
                self.NXs.append(0)
                continue
            IL_main = np.max(TdB[indices, ch])
            # 相邻串扰计算
            if ch > 0:
                IL_left = np.min(TdB[indices, ch - 1])#左相邻串扰为本通道在通带内的最大插入损耗与左边相邻通带内的最小插入损耗之差
                xt_left = IL_main - IL_left
            if ch < num_channels - 1:
                IL_right = np.min(TdB[indices, ch + 1])#右相邻串扰：本通道在通带内的最大插入损耗与右边相邻子通带内的最小插入损耗之差
                xt_right = IL_main - IL_right
            xt_adj = min(xt_left, xt_right)#相邻串扰为右相邻串扰和左相邻串扰中的最小值
            self.AXs.append( xt_adj)
            # 非相邻串扰计算：非相邻串扰为本通道在通带内的最大插入损耗与所有非相邻通带内的最小插入损耗之差
            non_adjacent_ils = []
            for other in range(num_channels):
                if abs(other - ch) > 1:
                   il_other = np.min(TdB[indices, other])
                   non_adjacent_ils.append(il_other)
            if non_adjacent_ils:
                xt_nonadj = IL_main - min(non_adjacent_ils)
            else:
                xt_nonadj = 0
            self.NXs.append(xt_nonadj)
        self.AX = min(self.AXs)#相邻通道串扰是各个通道相邻串扰的最小值。单位为分贝(dB)
        self.NX = min(self.NXs)#非相邻通道串扰为各个通道非相邻串扰的最小值，单位为分贝(dB)

        # 汇总指标值
        self.Value = [
            self.IL,
            self.NU,
            self.center_wavelength * 1e3,
            self.CS,
            self.BW3,
            self.BW1,
            self.AX,
            self.NX,
        ]

    def __str__(self):
        rows = [
            ['Insertion loss [dB]', self.IL],
            ['Loss non-uniformity [dB]', self.NU],
            ['Center wavelength [nm]', self.center_wavelength * 1e3],
            ['Channel spacing [nm]', self.CS],
            ['3dB bandwidth [nm]', self.BW3],
            ['1dB bandwidth [nm]', self.BW1],
            ['Adjacent crosstalk level [dB]', self.AX],
            ['Non-adjacent crosstalk level [dB]', self.NX],
        ]


        # 各通道的插入损耗、中心波长、3dB带宽、1dB带宽
        for idx in range(len(self.ILs)):
             rows.append([f'Channel {idx} IL [dB]', self.ILs[idx]])
             rows.append([f'Channel {idx} Center λ [nm]', self.center_wavelengths[idx] * 1e3])
             rows.append([f'Channel {idx} 3dB BW [nm]', self.BW3s[idx]])
             rows.append([f'Channel {idx} 1dB BW [nm]', self.BW1s[idx]])


        return tabulate(rows, headers=['Metric', 'Value'])

