# 导入 AWG 和仿真相关模块
from photfdtd.awg_python_main.awg.awg_simulation import AWG_Simulation


if __name__ == "__main__":
    """
    AWG参数设置：
    n_core:芯层折射率
    n_clad:包层折射率
    n_subs:衬底折射率
    lambda_c:中心波长
    channel_spacing:信道间隔
    FSR:自由频谱范围
    w:芯层宽度
    h:芯层厚度
    d:相邻阵列波导间距(中心—中心）
    Ni:输入波导数目
    Ng:阵列波导数目
    No:输出波导数目
    L_array:阵列波导长度
    L_FPR:自由传输区长度
    L_taper:波导taper长度
    W_taper:波导taper宽度
    type:解复用DEMUX还是复用MUX
    foldername:保存的文件名
    """

    # 创建仿真对象
    simulation = AWG_Simulation(
        n_clad=1.444, n_core=3.447, n_subs=1.444, lambda_c=1.55e-6, channel_spacing=0.8e-9, FSR=5e-9,
        Ni=1, No=4, w=0.4e-6, h=0.34e-6, Ng=88, m=155, L_FPR=100e-6, d=0.8e-6, delta_x=5.03e-6, L_array=20e-6,
        W_taper=1.2e-6, L_taper=10e-6,type="DEMUX", foldername='AWG_白刃_DEMUX', priority=1, axis='y'
    )

    # 绘制结构图
    simulation.plot_awg_structure()

    # 绘制电场分布图
    simulation.plot_field_distributions()
    # 运行仿真，得到光谱图
    simulation.run_simulation(iteration=1)#iteration:迭代次数，sweep_bandwidth：扫波长宽度，不设置默认FSR




