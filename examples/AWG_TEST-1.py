from photfdtd import Plot_AWG
import sys
# 添加模块路径
sys.path.append(r'D:/北交的三年/photfdtd项目/中期测试/photfdtd-main/photfdtd/awg_python_main')

# 导入 AWG 和仿真相关模块
from awg import *
from awg.core import *
from photfdtd.awg_python_main.AWGSimulation import AWG_Simulation
from photfdtd.awg_python_main.awg.material import Material

if __name__ == "__main__":

    # 创建仿真对象
    simulation = AWG_Simulation(
        n_clad=1.444, n_core=3.476, n_subs=1.444, lambda_c=1.55e-6,channel_spacing=1.6e-9,FSR= 29.812e-9,
        Ni=1, No=8, w=0.5e-6 ,h=0.22e-6,Ng =89,L_FPR =102.204e-6,d =1e-6,g=0.2e-6,L_array=20e-6,W_taper=2.4e-6, L_taper =12e-6,
        type="DEMUX",foldername = 'AWG_梁玥_DEMUX' ,priority = 1, axis = 'y'
    )
    # 绘制结构图
    simulation.plot_awg_structure()

    # 绘制电场分布图
    simulation.plot_field_distributions()
    # 运行仿真，得到光谱图
    simulation.run_simulation(iteration=1)#iteration:迭代次数，sweep_bandwidth：扫波长宽度




