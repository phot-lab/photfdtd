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

    def __init__(self,
                 material: str = 'materials/Si.csv',
                 data=None,
                 ):
        self.material = material
        import os
        current_directory = os.getcwd()
        parent_directory = os.path.dirname(current_directory)
        self.file = "%s\\photfdtd\\materials\\%s.csv" % (parent_directory, material)
        self.data = data
        self.fit_function_Reindex = None
        self.fit_function_Imindex = None
        self.fit()

    def fit(self):
        # 打开CSV文件并读取数据
        if self.data is None:
            self.data = np.genfromtxt(self.file, delimiter=',', skip_header=1)

        # 从读取的数据中提取wl, n和k的列
        self.wl_Reindex = self.data[:, 0]
        n = self.data[:, 1]
        # 调用scipy得到拟合函数
        self.fit_function_Reindex = interp1d(self.wl_Reindex, n, kind='cubic')
        if len(self.data[0]) == 4:
            # 若同时保存有消光系数k，则读取
            self.wl_Imindex = self.data[:, 2]
            k = self.data[:, 3]
            self.fit_function_Imindex = interp1d(self.wl_Imindex, k, kind='cubic')

    def plot(self,
             choice: bool = True,
             filepath: str = ''):
        """
        绘制曲线并保存
        :param choice: True表示绘制n，False表示绘制k （这个参数名起的很随意）
        :param filepath: 图片保存地址
        :return:
        """
        if choice:
            wl = self.wl_Reindex
            fit_function = self.fit_function_Reindex
            ylabel = 'Re(index)'
        else:
            wl = self.wl_Imindex
            fit_function = self.fit_function_Imindex
            ylabel = 'Im(index)'

        # 绘制拟合函数的曲线
        x = np.linspace(wl.min(), wl.max(), 1000)
        y = fit_function(x)

        plt.plot(x, y)
        plt.xlabel('Wavelength (μm)')
        plt.ylabel(ylabel)
        plt.savefig(fname='%s//wl-%s.png' % (filepath, ylabel))
        plt.show()

    def get_refractive_index(self, wavelength):
        wavelength *= 1e6 # From m unit to um unit
        index_Re = float(self.fit_function_Reindex(wavelength))
        try:
            index_Im = float(self.fit_function_Imindex(wavelength))
        except:
            index_Im = 0
        return index_Re, index_Im


if __name__ == "__main__":
    index_Si = Index('./materials/Si.csv')
    index_Si.fit()
    index_Si.plot(choice=True,
                  filepath='./')

    # 现在可以用拟合函数得到区域内一个波长下的折射率了
    wavelength_value = 1.6
    refractive_index_value = index_Si.fit_function_Reindex(wavelength_value)
    # k_value = index_Si.fit_function_Imindex(wavelength_value)

    print(refractive_index_value)
