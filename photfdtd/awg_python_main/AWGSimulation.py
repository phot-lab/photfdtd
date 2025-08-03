import os
import math
import numpy as np
import pandas as pd
from awg import *
from awg.core import *
from photfdtd import Plot_AWG


class AWG_Simulation:
    def __init__(self, n_clad, n_core, n_subs, lambda_c, channel_spacing,
                 Ni, No, w, h, Ng, L_FPR, d, L_array,W_taper, L_taper,
                 type, priority, axis, FSR=None,g=None,m=None, delta_x=None, foldername=None):

        self.n_core = n_core#芯层折射率
        self.n_clad = n_clad#包层折射率
        self.n_subs = n_subs#衬底折射率
        self.lambda_c = lambda_c#中心波长
        self.channel_spacing = channel_spacing#信道间隔
        self.FSR = FSR#自由频谱范围
        self.w = w#芯层宽度
        self.h = h#芯层厚度
        self.d = d#相邻阵列波导间距(中心—中心）
        self.Ni = Ni#输入波导数目
        self.Ng = Ng#阵列波导数目
        self.No = No#输出波导数目
        self.L_array = L_array#阵列波导长度
        self.L_FPR = L_FPR#自由传输区长度
        self.L_taper = L_taper#波导taper长度
        self.W_taper = W_taper#波导taper宽度
        self.type = type#解复用DEMUX还是复用MUX
        self.foldername = foldername#保存的文件名
        self.axis = axis
        self.priority = priority#优先级

        # 单位换算因子
        scale = 1e6  # 米转微米
        slab = Waveguide(clad=self.n_clad, core=self.n_core, subs=self.n_subs, h=self.h * scale, t=self.h * scale)
        ns = slab.index(self.lambda_c * scale, 1)[0]

        self.m = round(self.lambda_c / self.FSR) if m is None else m
        self.delta_x = self.m * self.L_FPR * self.channel_spacing / (ns * self.d) if delta_x is None else delta_x

        # 设置输入输出taper的宽度
        self.wi = self.w if self.W_taper in [0, None] else self.W_taper
        self.wo = self.w if self.W_taper in [0, None] else self.W_taper
        self.g = self.d - self.w if g is None else g  # 相邻阵列波导间距 gap


        # 初始化AWG系统模型的参数
        self.model = AWG(
            clad=self.n_clad,
            core=self.n_core,
            subs=self.n_subs,
            lambda_c=self.lambda_c * scale,
            channel_spacing=self.channel_spacing * scale,
            Ni=self.Ni,
            No=self.No,
            w=self.w * scale,
            m=self.m,
            h=self.h * scale,
            N=self.Ng,
            R=self.L_FPR * scale,
            d=self.d * scale,
            g=self.g*scale,
            di=self.delta_x * scale,
            do=self.delta_x * scale,
            wi=self.wi * scale,
            wo=self.wo * scale,
            L0=0,
            type=self.type
        )

        # 初始化仿真选项
        self.options = SimulationOptions()
        self.options.PhaseErrorVariance = 0
        self.options.ModeType = "gaussian"
        self.options.PropagationLoss = 0
        self.options.InsertionLoss = 0



        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)

        self.results = None

    def plot_awg_structure(self):#对称型结构，所以输入波导、输出波导、阵列波导的taper长一样
        awg_plotter = Plot_AWG(
            grid_xlength=math.sqrt(3) * self.L_FPR,
            grid_ylength=1,
            grid_zlength=1.2*self.L_FPR + 2 * self.L_array + 2*self.L_taper,
            grid_spacing=self.h,
            foldername=self.foldername,
            priority=self.priority,
            axis=self.axis,
            axis_number=0,
            lam0=self.lambda_c,
            d=self.d,
            delta_x=self.delta_x,
            w=self.w,
            h=self.h,
            L_FPR=self.L_FPR,
            Ng=self.Ng,
            Nch=self.No,
            L_array=self.L_array,
            W_taper_in=self.W_taper,
            L_taper_in=self.L_taper,
            W_taper_out=self.W_taper,
            L_taper_out=self.L_taper,
            W_taper_array=self.W_taper,
            L_taper_array=self.L_taper,
            refractive_index=self.n_core,
            background_index=self.n_clad
        )

        if not os.path.exists(awg_plotter.foldername):
            os.makedirs(awg_plotter.foldername)

        awg_plotter.plot_awg_out()
        awg_plotter.plot_awg_in()

        print(f"AWG结构图已保存至：{awg_plotter.foldername}")

    def plot_field_distributions(self):
        distribution = Distribution(self.model, output_dir=self.foldername, style="default")
        distribution.plot_output_distribution()
        print(f"Field distribution plots saved in '{self.foldername}' directory.")

    def run_simulation(self,iteration,sweep_bandwidth=None):
        # processed_values_list = []
        all_results = []
        labels = [
            "插入损耗 [dB]",
            "损耗不均匀性[dB]",
            "中心波长[nm]",
            "通道间隔[nm]",
            "3dB带宽[nm]",
            "10dB带宽[nm]",
            "相邻通道串扰",
            "非相邻通道串扰"
        ]
        data = np.zeros((iteration, 8))
        if sweep_bandwidth==None:
            self.sweep_bandwidth=self.FSR*1e6
        else:
            self.sweep_bandwidth=sweep_bandwidth


        for n in range(iteration):
            results = Spectrum(self.model, self.sweep_bandwidth, Options=self.options, Samples=100)
            measurements = Analyse(results)

            processed_values = []
            for val in measurements.Value:
                if isinstance(val, np.ndarray):
                    processed_values.append(val.flatten()[0].real)
                elif isinstance(val, complex):
                    processed_values.append(val.real)
                else:
                    processed_values.append(val)
            all_results.append(processed_values)

            data[n, :] = processed_values
            # processed_values_list.append(processed_values)

        # self.data = data
        # 转换为 DataFrame
        df_results = pd.DataFrame(all_results, columns=labels)
        df_results.index = [f"第{i+1}次" for i in range(iteration)]
        # 添加平均值
        df_results.loc["平均值"] = df_results.mean()
        # 另存“性能指标”列（行索引改为列）
        df_results = df_results.T
        df_results.insert(0, "性能指标", labels)  # 添加“性能指标”列
        # 保存 Excel
        excel_path = os.path.join(self.foldername, "性能参数结果.xlsx")
        df_results.to_excel(excel_path, index=False, engine='openpyxl')
        print("性能参数结果已导出为 Excel 文件：", excel_path)
        # average_values = bd.mean(processed_values_list, axis=0)
        #
        # df = pd.DataFrame({
        #     "性能指标": labels,
        #     "平均值": average_values
        # })
        #
        # excel_path = os.path.join(self.foldername, "性能参数结果.xlsx")
        # df.to_excel(excel_path, index=False, engine='openpyxl')
        # print("性能参数结果已导出为 Excel 文件：", excel_path)

        self.results = results
        self.data = np.array(all_results)

        # --- 画图部分 ---
        if self.results is not None:
            plt.figure()
            plt.plot(self.results.wavelength, 10 * np.log10(self.results.transmission.real))
            plt.ylim(-40, 0)
            plt.xlabel(r'波长（$\mu$m）')
            plt.ylabel("输出功率 (dB)")

            transmission_file = os.path.join(self.foldername, "transmission_spectrum.png")
            plt.savefig(transmission_file, dpi=300)
            plt.close()
            print("光谱图已保存为：", transmission_file)
        else:
            print("仿真结果尚未生成！")
