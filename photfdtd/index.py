import utils
import csv
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class Index:
    """
    从折射率库中读取某一材料的折射率数据，调用scipy库由离散的折射率数据得到拟合函数，并绘制和保存图像
    复折射率n' = n + ik，k又称消光系数
    file: .csv文件
    目前折射率库的规范是：第一列wl，第二列n，第三列wl，第四列k（有些材料k=0，因此只有前两列）
    为什么第三列也是wl？因为对于有些材料（比如H2O），k的波长与n的波长范围不一样
    """

    def __init__(
        self,
        file: str = "D:/下载内容/photfdtd-main/photfdtd/折射率数据/Si.csv",
    ):
        self.file = file

    def _fit_(self):
        # 打开CSV文件并读取数据
        data = np.genfromtxt(self.file, delimiter=",", skip_header=1)

        # 从读取的数据中提取wl, n和k的列
        self.wl_Reindex = data[:, 0]
        n = data[:, 1]
        # 调用scipy得到拟合函数
        self.fit_function_Reindex = interp1d(self.wl_Reindex, n, kind="cubic")
        if len(data[0]) == 4:
            # 若同时保存有消光系数k，则读取
            self.wl_Imindex = data[:, 2]
            k = data[:, 3]
            self.fit_function_Imindex = interp1d(self.wl_Imindex, k, kind="cubic")

    def _plot_(self, choice: bool = True, filepath: str = ""):
        """
        绘制曲线并保存
        :param choice: True表示绘制n，False表示绘制k （这个参数名起的很随意）
        :param filepath: 图片保存地址
        :return:
        """
        if choice:
            wl = self.wl_Reindex
            fit_function = self.fit_function_Reindex
            ylabel = "Re(index)"
        else:
            wl = self.wl_Imindex
            fit_function = self.fit_function_Imindex
            ylabel = "Im(index)"

        # 绘制拟合函数的曲线
        x = np.linspace(wl.min(), wl.max(), 1000)
        y = fit_function(x)

        plt.plot(x, y)
        plt.xlabel("Wavelength (μm)")
        plt.ylabel(ylabel)
        plt.savefig(fname="%s//wl-%s.png" % (filepath, ylabel))
        plt.show()


if __name__ == "__main__":
    index_Si = Index("Si.csv")
    index_Si._fit_()
    index_Si._plot_(choice=True, filepath="E:/campus/高速长距光纤传输系统软件设计平台/折射率数据/Si.csv")

    # 现在可以用拟合函数得到区域内一个波长下的折射率了
    wavelength_value = 1.6
    refractive_index_value = index_Si.fit_function_Reindex(wavelength_value)
    # k_value = index_Si.fit_function_Imindex(wavelength_value)

    print(refractive_index_value)
