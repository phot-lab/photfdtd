import numpy as np
from .simulation_options import SimulationOptions
from .AWG import *

class Simulate:
    """
    Simulate entire AWG from input to output at given wavelength.模拟整个 AWG 从输入到输出的过程，在给定波长下进行计算。

    INPUT:
        model  - AWG system to Simulate
        lmbda  - center wavelength [μm]
        _input - Number of input waveguide输入波导序号

    Optional:
        Points  - Number of point to sample over the differents fields在不同场上采样的点数，默认为 250
        Options - Using some custom simulation options using the SimulationOptions function使用自定义仿真选项，通过 SimulationOptions 函数提供

    OUTPUT:
        None

    ATTRIBUTE:
        inputField   - Field at the input waveguide输入波导处的场分布
        arrayField   - Field at the end of the arrayed section阵列部分末端的场分布
        outputField  - Field at the output waveguide输出波导处的场分布
        transmission - Transmission for each AWG ouput channel每个 AWG 输出通道的传输情况
        lmbda        - Wavelenght use for the simulation用于仿真的波长
    """
    def __init__(self,model,lmbda,_input = 0,**kwargs):

        _in = kwargs.keys()
        points = kwargs["Points"] if "Points" in _in else 250# 设置默认采样点数
        Options = kwargs["Options"] if "Options" in _in else SimulationOptions()# 获取仿真选项，默认为 SimulationOptions() 类的实例
        if Options.CustomInputField != []:# 如果自定义输入场存在，则使用自定义输入场；否则使用默认模式类型和点数
            F_iw = iw(model,lmbda,_input,Options.CustomInputField)
        else:
            F_iw = iw(model,lmbda,_input, ModeType = Options.ModeType, points = points)
        # 计算第一阶段的场分布（通过 FPR1）
        F_fpr1 = fpr1(model,lmbda,F_iw,points= points)
        # 计算阵列波导的场分布
        F_aw= aw(model,lmbda,F_fpr1, ModeType = Options.ModeType,
                PhaseErrorVar = Options.PhaseErrorVariance, InsertionLoss = Options.InsertionLoss,
                PropagationLoss = Options.PropagationLoss)
        # 计算第二阶段的场分布（通过 FPR2）
        F_fpr2 = fpr2(model,lmbda,F_aw, points = points)
        # 计算输出波导的T
        F_ow = ow(model,lmbda,F_fpr2, ModeType = Options.ModeType)



        # 将仿真结果赋值给对象的属性
        self.inputField = F_iw
        self.slabField=F_fpr1
        self.arrayField = F_aw
        self.outputField = F_fpr2
        self.transmission = F_ow
        self.lmbda = lmbda



