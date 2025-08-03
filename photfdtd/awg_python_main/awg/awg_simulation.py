import os
import math
import numpy as np
import pandas as pd
from tqdm import trange
from photfdtd import Plot_AWG
from photfdtd.awg_python_main.awg import AWG, Simulate, SimulationOptions, Spectrum, Analyse, Distribution, Waveguide
import matplotlib.pyplot as plt
from photfdtd.awg_python_main.awg.material.material import Material



class AWG_Simulation:
    def __init__(self, n_clad, n_core, n_subs, lambda_c, channel_spacing,
                 Ni, No, w, h, Ng, L_FPR, d, L_array,W_taper, L_taper,
                 type, priority, axis, FSR=None,g=None,m=None, delta_x=None, foldername=None):

        self.n_core = n_core #芯层折射率
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
        self.scale = 1e6  # 米转微米
        # 设置中文字体支持
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False




        # 设置输入输出taper的宽度
        self.wi = self.w if self.W_taper in [0, None] else self.W_taper
        self.wo = self.w if self.W_taper in [0, None] else self.W_taper
        self.g = self.d - self.w if g is None else g  # 相邻阵列波导间距 gap

        if isinstance(self.n_core, (int, float)):
            self.n_core = self.n_core
        else:
            material_core = Material(self.n_core)
            self.n_core = float(material_core.index(self.lambda_c*self.scale))  # λ单位是μm
        self.refractive_index = self.n_core

        if isinstance(self.n_clad, (int, float)):
            self.n_clad = self.n_clad
        else:
            material_clad = Material(self.n_clad)
            self.n_clad = float(material_clad.index(self.lambda_c*self.scale))  # λ单位是μm
        self.background_index = self.n_clad
        if isinstance(self.n_subs, (int, float)):
            self.n_subs  = self.n_subs
        else:
            material_subs = Material(self.n_subs )
            self.n_subs  = float(material_subs.index(self.lambda_c*self.scale))  # λ单位是μm


        slab = Waveguide(clad=self.n_clad, core=self.n_core, subs=self.n_subs, h=self.h * self.scale, t=self.h *self.scale)
        ns = slab.index(self.lambda_c * self.scale, 1)[0]
        self.m = round(self.lambda_c / self.FSR) if m is None else m
        self.delta_x = self.m * self.L_FPR * self.channel_spacing / (ns * self.d) if delta_x is None else delta_x




        # 初始化AWG系统模型的参数
        self.model = AWG(
            clad=self.n_clad,
            core=self.n_core,
            subs=self.n_subs,
            lambda_c=self.lambda_c * self.scale,
            channel_spacing=self.channel_spacing *self.scale,
            Ni=self.Ni,
            No=self.No,
            w=self.w * self.scale,
            m=self.m,
            h=self.h * self.scale,
            N=self.Ng,
            R=self.L_FPR * self.scale,
            d=self.d *self.scale,
            g=self.g*self.scale,
            di=self.delta_x * self.scale,
            do=self.delta_x * self.scale,
            wi=self.wi * self.scale,
            wo=self.wo *self.scale,
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
            refractive_index=self. refractive_index,
            background_index=self.background_index
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

    def run_simulation(self, iteration, sweep_bandwidth=None):
        data = np.zeros((iteration, 8))
        all_channel_data = []
        # 确保输出文件夹存在
        os.makedirs(self.foldername, exist_ok=True)

        if sweep_bandwidth is None:
           self.sweep_bandwidth = self.FSR * 1e6
        else:
           self.sweep_bandwidth = sweep_bandwidth

        for n in range(iteration):
            results = Spectrum(
               self.model,
               self.sweep_bandwidth,
               Options=self.options,
               Samples=100,
               foldername=self.foldername,
               Ng=self.Ng,
               delta_x=self.delta_x * self.scale,
               d=self.d * self.scale,
               m=self.m
             )
            measurements = Analyse(results, self.model.lambda_c, self.model.channel_spacing)


            for ch in range(len(measurements.ILs)):
                 all_channel_data.append({
                    'Iteration': n + 1,
                    'Channel': ch,
                    'Insertion loss [dB]': measurements.ILs[ch],
                    'Center wavelength [nm]': measurements.center_wavelengths[ch] * 1e3,
                    '3dB bandwidth [nm]': measurements.BW3s[ch],
                    '1dB bandwidth [nm]': measurements.BW1s[ch],
                  })

            # 保存整体性能指标
            data[n, :] = measurements.Value

            # 保存每次迭代输出功率图
            results.export_to_excel(filename=f"iter{n+1}_output_power_dB.xlsx")


         #汇总性能指标
        summary_keys = [
           "插入损耗 [dB]",
           "损耗不均匀性 [dB]",
           "中心波长 [nm]",
           "通道间隔 [nm]",
           "3dB带宽 [nm]",
           "1dB带宽 [nm]",
           "相邻通道串扰 [dB]",
           "非相邻通道串扰 [dB]"
         ]
        performance_table = {}
        for idx, key in enumerate(summary_keys):
             performance_table[key] = list(data[:, idx])

        # 汇总每个通道的数据（IL/λ/BW）
        channel_df = pd.DataFrame(all_channel_data)
        for ch in range(self.model.No):
           performance_table[f"IL 通道{ch} [dB]"] = channel_df[channel_df["Channel"] == ch]["Insertion loss [dB]"].tolist()
           performance_table[f"λ 通道{ch} [nm]"] = channel_df[channel_df["Channel"] == ch]["Center wavelength [nm]"].tolist()
           performance_table[f"3dB带宽 通道{ch} [nm]"] = channel_df[channel_df["Channel"] == ch]["3dB bandwidth [nm]"].tolist()
           performance_table[f"1dB带宽 通道{ch} [nm]"] = channel_df[channel_df["Channel"] == ch]["1dB bandwidth [nm]"].tolist()

         #  构建 DataFrame 表格：每一行是一个指标，每列是一轮迭代
        performance_df = pd.DataFrame(performance_table).T
        performance_df.columns = [f"第{i+1}次" for i in range(iteration)]
        performance_df["平均值"] = performance_df.mean(axis=1)
        performance_df.insert(0, "性能指标", performance_df.index)
        performance_df.reset_index(drop=True, inplace=True)

         # 导出 Excel
        result_excel_path = os.path.join(self.foldername, "性能总表.xlsx")
        performance_df.to_excel(result_excel_path, index=False)
        print(f"✅ 所有性能数据已导出至：{result_excel_path}")

         # 画光谱图
        if results is not None:
           plt.figure()
           plt.plot(results.wavelength, 10 * np.log10(results.transmission.real))
           plt.ylim(-90, 0)
           plt.xlabel(r'波长（$\mu$m）')
           plt.ylabel("输出功率 (dB)")
           transmission_file = os.path.join(self.foldername, "transmission_spectrum.png")
           plt.savefig(transmission_file, dpi=300)
           plt.close()
           print("光谱图已保存为：", transmission_file)
        else:
           print("仿真结果尚未生成！")
