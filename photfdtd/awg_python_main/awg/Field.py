from .core import *
import numpy as np
from tabulate import tabulate

def DataFormat(D,sz):# 数据格式化函数
    if len(D) == 0:
        D = np.zeros(sz, dtype = complex)[0]# 如果数据为空，返回一个零矩阵
        return D

    shape_D = [1]

    if np.shape(D)[0]> 1:# 如果 D 的第一维大于 1
        try:
            shape_D = [len(i) for i in D]# 尝试获取 D 的每一维的长度
        except TypeError:
            shape_D.append(len(D))# 如果 D 不能被迭代，添加 D 的长度
    else:
        shape_D.append(np.shape(D)[0])# 如果 D 是一维数组，添加它的长度

    s =[]

    for i in sz:
        if i > 1:
            s.append(True)
        else:
            s.append(False)

    if False not in s:# 检查输入数据和坐标点是否匹配
        if shape_D != sz:
            print(f"Shape of D: {shape_D}, Expected shape: {sz}")
            raise ValueError("Wrong data format. The field must contain the same number of rows as the y-coordinate points and the same number of columns as the x-coordinate points.")
        if len(D) != max(sz):
            raise ValueError("Wrong data format. Expecting field data to be the same size as the coordinate elements.")

    return D

class Field:
    """
    INPUT:

    X - Coordinate data, one of:
        vector  - A one dimensional vector of x coordinates.
        cell	- A cell array containing x and y coordinates: {x, y}.
            Note: for representing only y coordinates, pass a
            cell array of the form {[], y}.

    E - Electric field data.
    H - (optional) magnetic field data. Both of these fields can be
        one of:
            vector  - A one dimensional vector of data points. In this
                case, the data will be mapped to the x-component
                of the field by default.
            cell	- A cell array containing x, y and z component data
                in the form: {Ux, Uy, Uz}. For omitting data of
                certain components, use empty arrays. For example
                H = {[],Hy,[]}.
    """
    """
    输入：
    X - 坐标数据，可以是以下其中之一：
        - 向量：一个包含 x 坐标的一维向量。
        - 单元格：一个包含 x 和 y 坐标的单元格数组：{x, y}。
            注意：如果仅表示 y 坐标，传入格式为 {[], y}。

    E - 电场数据。
    H - （可选）磁场数据。电场和磁场数据都可以是以下之一：
        - 向量：一个包含数据点的一维向量，默认映射到场的 x 分量。
        - 单元格：一个包含 x、y 和 z 分量数据的单元格数组，格式为 {Ux, Uy, Uz}。如果某个分量数据缺失，可以使用空数组。例如 H = {[], Hy, []}。
    """
    def __init__(self,X, E, H = []):
        # print("Type of X:", type(X))  # 打印 X 的类型
        # print("Shape of X:", np.shape(X))
        # print("Shape of E:", np.shape(E))
        # print("Shape of H:", np.shape(H))

        self.scalar = True# 默认电场是标量场
        if len(X) < 1:# 检查坐标 X 的长度，必须提供坐标数据
            raise ValueError("At least one coordinate vector must be provided.")

        self._y = []# y 坐标初始化为空
        self.dimens = 1## 默认是1维数据

        if type(X) == tuple:# 如果 X 是元组，说明是一个包含 x 和 y 坐标的情况
            self._x = X[0]# 设置 x 坐标

            if len(X) > 1 :# 如果有多个坐标，说明是三维数据
                self._y = X[1]
                self.dimens = 3# 三维数据
                if len(self._x) == 0:
                    self.dimens = 2# 如果没有 x 坐标，设置为二维
                if len(self._y) == 0:
                    self.dimens = 1# 如果没有 y 坐标，设置为一维

        elif len(list(np.shape(X))) > 1: # 如果 X 不是元组，则检查是否为二维数据，必须是一维向量
            raise ValueError("Wrong coordinate format. Must be a 1-D vector.")
        else:
            self._x = X# 直接设置 x 坐标

        if (len(self._x) == 0) and (len(self._y) == 0):# 如果没有提供 x 和 y 坐标，则抛出错误
            raise Error("At least one coordinate vector must be provided.")

        if False in np.isreal(self._x) or False in np.isreal(self._y):# 检查坐标向量是否是实数值
            raise ValueError("Cordinate vectors must be real numbers.")
        # 如果是1维数据，初始化 _y 为长度与 _x 相同的零向量,并命名为 _y0
        if self.dimens == 1 and len(self._y) == 0:
           self._y0 = np.zeros_like(self._x)

        self.Xdata = np.array([self._x,self._y0])# 将 x 和 y 坐标数据组合成一个二维数组
        # print("Shape of self.Xdata:",np.shape(self.Xdata))

        # 设置数据的形状
        sz = [max([1,1][i],[len(self._y),len(self._x)][i]) for i in range(2)]

        if len(E) < 1:# 检查电场数据 E 是否为空
            raise ValueError("Electric field data is empty.")
        # 初始化电场的各分量
        self._Ex = []
        self._Ey = []
        self._Ez = []

        if type(E) == tuple:# 如果电场数据是元组，则按分量进行处理
            if len(E) > 0:
                self.scalar = False# 如果是元组，则为矢量场
                self._Ex = E[0] if self.dimens > 2 else np.conj(E[0])# 设置 x 分量
            if len(E) > 1:
                self._Ey = E[1] if self.dimens > 2 else np.conj(E[1])# 设置 y 分量
            if len(E) > 2:
                self._Ez = E[2] if self.dimens > 2 else np.conj(E[2])# 设置 z 分量
        else:
            self.scalar = True# 如果只有一个分量，则为标量场
            self._Ex = E if self.dimens > 2 else np.conj(E)# 设置电场的 x 分量


        # 将电场数据格式化
        self.Edata = (DataFormat(self._Ex,sz),
                    DataFormat(self._Ey,sz),
                    DataFormat(self._Ez,sz))
        # 将电场数据转换为数组格式
        self._Ex = list_to_array(self.Edata[0])
        self._Ey = list_to_array(self.Edata[1])
        self._Ez = list_to_array(self.Edata[2])


        # 处理磁场，跟电场一样的操作
        self._Hx = []
        self._Hy = []
        self._Hz = []

        if type(H) == tuple:
            if len(H) > 0:
                self.scalar = False
                self._Hx = H[0]

            if len(H) > 1:
                    self._Hy = H[1]

            if len(H) > 2:
                self._Hz = H[2]
        else:
            self.scalar = True
            self._Hx = H

        self.Hdata = (DataFormat(self._Hx,sz),
                    DataFormat(self._Hy,sz),
                    DataFormat(self._Hz,sz))


        self._Hx = list_to_array(self.Hdata[0])
        self._Hy = list_to_array(self.Hdata[1])
        self._Hz = list_to_array(self.Hdata[2])

        self.salut = 5

    def poynting(self):
        """
        Returns the Poynting vector component z (transverse power density)返回泊松分量 z（横向功率密度）
        """

        if self.hasMagnetic() :
            return  self.Ex*np.conjugate(self.Hy) - self.Ey*np.conjugate(self.Hx)
        else:

            return self.Ex*np.conjugate(self.Ex)

    def power(self):
        """
        Return power carried by the field in W or W/μm返回电场携带的功率，单位是 W 或 W/μm
        """
        if self.dimens == 3:
            return np.trapz(np.trapz(self._y, self.poynting()),self._x)
        if self.dimens == 1:
            # print(self.poynting(),self._x)
            return np.trapz(self.poynting(),self._x)
        else:
            return np.trapz(self.poynting(),self._y)


    def normalize(self,P = 1):
        """
        Normalize the field relatively to it's power.对电场进行归一化，使其相对于功率进行标准化。

        P - Normalized Value 标准化值
        """
        P0 = self.power()
        # 检查 P0 的有效性
        if P0 is None or np.isnan(P0) or np.isinf(P0):
           raise ValueError(f"Invalid P0 detected: {P0}")
        if P0 == 0:
           raise ValueError("P0 is zero, which will cause division by zero!")

        for j in range(len(self.Edata)):
            for i in range(len(self.Edata[j])):
                epsilon = 1e-10#添加小偏移量避免零除
                self.Edata[j][i] = self.Edata[j][i] * np.sqrt(P / (P0 + epsilon))

                # self.Edata[j][i] = self.Edata[j][i]*np.sqrt(P/P0)
        for j in range(len(self.Hdata)):
            for i in range(len(self.Hdata[j])):
                self.Hdata[j][i] = self.Hdata[j][i]*np.sqrt(P/P0)
        return self

    def hasElectric(self):
        """
        Look if any electric field is define.返回是否定义了电场数据。
        """
        return bool(np.any([self.Edata]))

    def hasMagnetic(self):
        """
        Look if any magnetic field is define. 返回是否定义了磁场数据。
        """
        return bool(max(np.any(i) for i in self.Hdata))


    def getMagnitudeE(self):
        """
        Return the electric field magnitude.返回电场的幅度（根方差）。
        """
        return [
            sum(abs(self.Edata[j][i]) ** 2 for j in range(len(self.Edata))) ** 0.5
            for i in range(len(self.Edata[0]))
        ]

    def getMagnitudeH(self):
        """
        Return the magnetic field magnitude.返回磁场的幅度（根方差）。
        """
        return [
            sum(abs(self.Hdata[j][i]) ** 2 for j in range(len(self.Hdata))) ** 0.5
            for i in range(len(self.Hdata[0]))
        ]

    def isScalar(self):
        """
        Look if there is only one component field.返回是否为标量场。
        """
        return self.scalar

    def hasX(self):
        """
        Look if there is any field dendity over X.返回是否定义了电场的 x 分量。
        """
        return self.dimens in [1, 3]

    def hasY(self):
        """
        Look if there is any field density over Y.返回是否定义了电场的 y 分量。
        """
        return self.dimens in [2, 3]

    def isBidimensional(self):
        """
        Look if there are X and Y field density.
        """
        return self.dimens >2

    def isElectroMagnetic(self):
        """
        Look if there is electric and magnetic field.
        """
        return self.hasElectric() and self.hasMagnetic()

    def getSize(self):
        """
        Return the field size.
        """
        return [max([1,1][i],[len(self._y),len(self._x)][i]) for i in range(2)]

    def offsetCoordinates(self,dx = 0,dy = 0):#将 self.Xdata 中的坐标点偏移 dx 和 dy
        if len(self.Xdata[0]) != 0:
            self.Xdata[0] = [i+dx for i in self.Xdata[0]]
        if len(self.Xdata[0]) != 0:
            self.Xdata[1] = [i+dy for i in self.Xdata[1]]
        return self

    def __str__(self):
        x = f"[{self.Xdata[0][0]},...,{self.Xdata[0][-1]}]" if self.hasX() else "None"
        y = f"[{self.Xdata[1][0]},...,{self.Xdata[1][-1]}]" if self.hasY() else "None"
        return tabulate([['X', x, "X values"], ['Y', y, "Y values"],
                    ['E', self.E.shape, "Electrical field shape"],['H', self.H.shape, "Magnetic field shape"]], headers=['parameters', 'Value', 'definition'])




    ### Define getter and setter for the Field object ###

    @property
    def x(self):
        return self.Xdata[0]

    @property
    def y(self):
        return self.Xdata[1]

    @property
    def E(self):
        return self.Edata[0] if self.isScalar else self.Edata

    @property
    def Ex(self):
        return self.Edata[0]

    @property
    def Ey(self):
        return self.Edata[1]

    @property
    def Ez(self):
        return self.Edata[2]

    @property
    def H(self):
        return self.Hdata[0] if self.isScalar else self.Hdata

    @property
    def Hx(self):
        return self.Hdata[0]

    @property
    def Hy(self):
        return self.Hdata[1]

    @property
    def Hz(self):
        return self.Hdata[2]
