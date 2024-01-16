import numpy as np
# 计算MMI参数
ns = 1  # 包层（限制层）折射率（论文里为nc）
nf = 3.47  # 折射率（论文里为nr）
lambda0 = 1550e-9  # 入射光波长
pi = np.pi
k0 = 2 * pi / lambda0
Wm = 56 * 20 * 10 ** -9  # 多模波导宽度 单位m
grid_spacing = 20e-9
c0 = 299792458

# TE Mode，对于TE模，sigma = 0 ，对于TM模，sigma = 1
sigma = 1
We = Wm + (lambda0 / pi) * ((ns / nf) ** (2 * sigma)) * ((nf ** 2 - ns ** 2) ** (-1 / 2))  # 多模波导有效宽度
print("TE: 多模波导有效宽度We, effective width =  ", We)
beta = np.zeros(5)
neffapx = np.zeros(5)
for i in range(5):
    beta[i] = k0 * nf - (((i + 1) ** 2) * pi * lambda0) / ((We ** 2) * 4 * nf)
    neffapx[i] = beta[i] / k0
    # kc = (i+1)*pi/We #多模波导水平方向波数
    print("Approximate_Neff = %4.3f" % (neffapx[i]))

Lpi_apx = np.pi / (beta[0] - beta[1])
# Lpi_apx = 4*nf*We**2/(3*lambda0) #𝐿𝜋 0阶与1阶导模的共振长度,两种算法是一样的
print(" 𝐿𝜋 = %4.2f um" % (1e6 * Lpi_apx))

Lpi = int(Lpi_apx / grid_spacing)
W = int(Wm / grid_spacing)

# Lpi_apx = Lpi_apx*3 / 4 # TODO :为什么要乘以3/4
n = int(input('输入端口数：'))
m = int(input('输出端口数：'))

W_wg = (1 / ((2 * m) ** (1 / 4))) * np.sqrt(lambda0 * We / neffapx[0])  # 输入、输出波导的宽度
width_ports = int(W_wg / grid_spacing)

if n == 1:
    print('多模波导长度应为：%.2fum, 即%d个网格' % (1e6 * 3 * Lpi_apx / 4 / m, int(3 * Lpi_apx / 4 / m / grid_spacing)))
    print('多模波导宽度应为：%.2fum, 即%d个网格' % (1e6 * Wm, int(Wm / grid_spacing)))
    print('多模波导有效宽度We应为：%.2fum, 即%d个网格' % (1e6 * We, int(We / grid_spacing)))
    print('输入、输出波导宽度应为：%.2fum, 即%d个网格' % (1e6 * W_wg, int(width_ports)))
if n == 2:
    print('多模波导长度应为：%.2fum, 即%d个网格' % (1e6 * Lpi_apx / n, int(Lpi_apx / n / grid_spacing)))
    print('多模波导宽度应为：%.2fum, 即%d个网格' % (1e6 * Wm, int(Wm / grid_spacing)))
    print('多模波导有效宽度We应为：%.2fum, 即%d个网格' % (1e6 * We, int(We / grid_spacing)))
    print('输入、输出波导宽度应为：%.2fum, 即%d个网格' % (1e6 * W_wg, int(width_ports)))
if n != 1 and n != 2:
    W_wg = (1 / ((2 * n) ** (1 / 4))) * np.sqrt(lambda0 * We / neffapx[0])  # 输入、输出波导的宽度
    width_ports = int(W_wg / grid_spacing)
    # (这个公式是怎么来的？)
    print('多模波导长度应为：%.2fum, 即%d个网格' % (1e6 * 3 * Lpi_apx / n, int(3 * Lpi_apx / n / grid_spacing)))
    # print('输入、输出波导宽度应为：%.2fum, 即%d个网格' % (1e6 * W_wg, int(width_ports)))
    print('多模波导宽度应为：%.2fum, 即%d个网格' % (1e6 * Wm, int(Wm / grid_spacing)))
    print('多模波导有效宽度We应为：%.2fum, 即%d个网格' % (1e6 * We, int(We / grid_spacing)))
