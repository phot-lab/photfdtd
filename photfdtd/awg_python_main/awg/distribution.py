import numpy as np
from .AWG import *
from .core import *
from .plotfield import plotfield
import .Simulate import Simulate
import .SimulationOptions import SimulationOptions
import matplotlib.pyplot as plt
import matplotlib
import os
from scipy.optimize import curve_fit

def gaussian(x, a, x0, sigma):
        return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

class Distribution:
    """
    用于计算并绘制不同波长在输出端的电场分布（if解复用DEMUX用）。

    参数：
        model            - AWG 模型
        lambda_c - 中心波长（单位：μm）
        channel_spacing   - 信道间隔（单位：μm）
        No      - 信道数量(即输出波导个数）
        type    -解复用"DEMUX" /复用 "MUX"
        kwargs           - 其他仿真参数，例如 Points, Options
    """

    def __init__(self, model,output_dir, style,**kwargs):
        self.model = model
        self.lambda_c = model.lambda_c
        self.channel_spacing =model.channel_spacing
        self.No =model.No
        self.Ni = model.Ni
        self.type=model.type
        self.kwargs = kwargs
        self.style=style
        self.output_fields = []  # 存储所有波长的输出场分布
        self.output_dir = output_dir # 设置输出文件夹

        # 计算波长列表
        self.wavelengths = self.compute_wavelengths()
        self.simulate_wavelengths()
        # 确保输出文件夹存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def compute_wavelengths(self):
        """
        计算信道的波长列表，中心波长对称分布。
        """
        if self.No > self.Ni:
           half_N = self.No // 2
           N_range = self.No  # 取较大的 No 作为 range
        else:
           half_N = self.Ni // 2
           N_range = self.Ni  # 取较大的 Ni 作为 range
        if self.style == "same":
           # 如果 style 为 "same"，生成与 self.lambda_c 相同的波长列表
            return [self.lambda_c] * half_N*2

        else: # 如果 style 为 "default",生成一列不同波长列表
            return [self.lambda_c + (i - half_N) * self.channel_spacing for i in range(1,N_range+1)]



    def simulate_wavelengths(self):
        """对所有波长进行仿真并存储输出场。"""
        print("wavelegths:",self.compute_wavelengths())
        for i, lmbda in enumerate(self.wavelengths):
            print(f"目前计算的波长是：{lmbda}")  # 输出当前波长
            if self.type == "DEMUX":#解复用
                _input = 0  # 对应同一个输入波导（默认第一个波导）
            elif self.type == "MUX":#复用
                _input =-i+(self.Ni-1)  # 一个波长一个输入波导
            else:
                raise ValueError("Invalid type. Please use 'DEMUX' or 'MUX'.")

            simulation = Simulate(self.model, lmbda, _input, points=10000000,**self.kwargs)
            # 绘制并保存 inputField、slabField 和 arrayField ,outputField图像
            self.plot_field(simulation.inputField, "input", lmbda)
            self.plot_field(simulation.slabField, "slab", lmbda)
            self.plot_field(simulation.arrayField, "array", lmbda)
            self.plot_field(simulation.outputField, "output", lmbda)
            self.output_fields.append(simulation.outputField)





    def plot_output_distribution(self):
        """
        绘制所有波长的输出场分布。
        纵坐标：|E|^2，即电场的强度平方
        横坐标：x (μm)，即输出端位置
        不同波长的结果放在同一张图里，并用不同颜色的曲线表示
        """
        plt.figure(figsize=(8, 6))  # 设置图像大小
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False
        colormap = plt.cm.viridis  # 选取颜色映射方案
        colors = colormap(np.linspace(0, 1, len(self.wavelengths)))  # 为每个波长分配不同颜色
        peak_positions = []  #先初始化为一个空列表


        for i, (wavelength, field) in enumerate(zip(self.wavelengths, self.output_fields)):
            x_vals = field.x  # 获取 x 轴坐标
            intensity = np.abs(field.E) ** 2  # 计算 |E|^2
            max_idx = np.argmax(intensity)  # 找到强度平方最大值的索引
            window = 10  # 左右各取10个点，可调整
            start = max(max_idx - window, 0)
            end = min(max_idx + window + 1, len(x_vals))
            x_fit = x_vals[start:end]
            y_fit = intensity[start:end]

            try:
                popt, _ = curve_fit(gaussian, x_fit, y_fit, p0=[np.max(y_fit), x_vals[max_idx], 1.0])
                refined_peak = popt[1]
            except RuntimeError:
                refined_peak = x_vals[max_idx]  # 拟合失败就退回原值
            peak_positions.append(refined_peak)
            print(f"波长 {wavelength:.5f} μm 的最大 |E|^2 出现在 x ≈ {refined_peak:.3f} μm")
            plt.plot(x_vals, intensity, label=f"{wavelength:.5f} μm", color=colors[i], linewidth=1.5)  # 绘制曲线

        if len(peak_positions) > 1:
            peak_positions = np.array(peak_positions)
            deltas = np.diff(peak_positions)
            print("相邻波长对应的输出位置差（μm）:", np.round(deltas, 3))

        plt.xlabel("x (μm)")
        plt.ylabel(r"$|E|^2$")  # 使用 LaTeX 语法
        plt.title("输出端光场分布")
        plt.legend(title="波长(μm)", fontsize=8)  # 添加图例
        plt.grid(True, linestyle="--", alpha=0.6)  # 添加网格
        # 保存图像到指定文件夹
        save_path = os.path.join(self.output_dir, "output_distribution.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")  # 保存图片
        plt.close()  # 关闭图像

    def plot_field(self, field, field_type,wavelength):
        """绘制场并保存图像"""
        # 设置图形的宽度和高度
        plt.rcParams["figure.figsize"] = 20, 10
        plt.rcParams.update({'font.size': 15})

        # 选择绘制方式
        if field_type in ["slab", "array","output"]:
            plotfield(field, PlotPhase=True, UnwrapPhase=True, NormalizePhase=True)
        else:
            plotfield(field)

        # 设置保存图像的路径
        save_path = os.path.join(self.output_dir, f"{field_type}_{wavelength:.5f}um.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()  # 关闭当前图像




