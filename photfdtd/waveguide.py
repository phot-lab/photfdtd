import numpy as np


class Waveguide:
    """
    矩形波导
    xlength:
    ylength:
    zlength:
    x,y,z: 中心位置坐标
    width：波导宽度(在矩形波导中，波导宽度没有意义，它只是作为父类保留这个参数)
    refractive_index: 折射率
    background_index: 环境折射率
    name:名称
    """
    # TODO: fdtd包绘制场的代码很有问题，在3d仿真时不能正确显示
    # TODO: z方向空间步长单独设置？
    # TODO: 如何保存整个仿真而不仅仅是监视器数据？
    # TODO: 在波导被添加进grid后，x,y,z仍然会从中心坐标变成角点坐标，如何修复这一点？
    def __init__(
            self,
            xlength=200,
            ylength=20,
            zlength=20,
            x=100,
            y=30,
            z=30,
            width=10,
            name="waveguide",
            refractive_index=3.47,
            background_index=1
    ):

        self.xlength = xlength
        self.ylength = ylength
        self.zlength = zlength
        self.x = x - int(xlength / 2)
        self.y = y - int(ylength / 2)
        self.z = z - int(zlength / 2)
        self.width = width
        self.name = name
        self.refractive_index = refractive_index
        self.background_index = background_index

        self._compute_permittivity()
        self._set_objects()

    def _compute_permittivity(self):
        """矩形波导"""
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
        permittivity += self.refractive_index ** 2

        self.permittivity = permittivity

    def _set_objects(self):
        self._internal_objects = [self]

    def _negate_binary_matrix(self,
                              matrix):
        # 输入矩阵，得到相反数
        # 创建一个新的矩阵，用于存储相反数后的结果
        result_matrix = []

        # 遍历原始矩阵的每一行
        for row in matrix:
            # 创建一个新的行，用于存储相反数后的结果行
            result_row = []

            # 遍历原始矩阵中当前行的每个元素
            for value in row:
                # 将0变为1，将1变为0
                result_row.append(1 - value)

            # 将相反数后的结果行添加到结果矩阵中
            result_matrix.append(result_row)

        return result_matrix
