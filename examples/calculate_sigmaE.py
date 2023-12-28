from scipy import integrate
from photfdtd import constants
import math
# 为pml边界计算sigmaE_max
epsilon0 = constants.eps0
c = constants.c


def calculate_R(d, sigmaE_max):
    def integrand(x):
        return (x / d) ** 2

    # 定义积分区间
    lower_limit = 0
    upper_limit = d

    # 计算定积分
    result_i, error = integrate.quad(integrand, lower_limit, upper_limit)

    return math.exp(-2 * sigmaE_max * result_i / (epsilon0 * c * n))


def calculate_sigmaEmax(R, d):
    """
    为pml边界计算sigmaE_max
    @param R: 反射系数，一般选择尽可能趋近于0
    @param d: pml边界厚度，单位为空间步长
    @return: sigmaE_max
    """
    return (3 / 2) * epsilon0 * c * n * math.log(1 / R) / d


n = 1.445
R = calculate_R(d=0.2 * 15, sigmaE_max=2)
sigmaE_max = calculate_sigmaEmax(R=1e-10, d=0.2 * 15)

print(f"The result of R is: {R}")
print(f"The result of sigmaE_max is: {sigmaE_max}")
