import numpy as np
from .waveguide import Waveguide


class Arc(Waveguide):
    """圆弧
    outer_radius: 外环半径
    length: 波导y厚度
    x,y,z: 圆心位置
    width: 波导宽度
    refractive_index:折射率
    name: 名称
    angle_phi: 与x轴正方向夹角, 单位: 角度
    angle_psi: 张角
    background_index: 环境折射率
    angle_to_radian: bool: True表示从角度转弧度
    """

    # FIXME: 在圆弧跨越x=0时存在问题
    def __init__(
            self,
            outer_radius: int or float = 60,
            ylength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width: int or float = 20,
            refractive_index: float = 3.47,
            name: str = "arc",
            angle_phi: float = 0,
            angle_psi: float = 0,
            angle_to_radian: bool = True,
            grid=None,
    ) -> None:
        angle_phi = angle_phi % 360
        if angle_phi < 0:
            angle_phi += 360

        outer_radius, width = grid._handle_unit([outer_radius, width], grid_spacing=grid._grid.grid_spacing)
        self.outer_radius = outer_radius
        if angle_to_radian:
            self.phi = np.radians(angle_phi)
            self.psi = np.radians(angle_psi)
        else:
            self.phi = angle_phi
            self.psi = angle_psi

        super().__init__(xlength=outer_radius, ylength=ylength, zlength=outer_radius, x=x,
                         y=y, z=z, width=width, name=name, refractive_index=refractive_index, reset_xyz=False,
                         grid=grid)


    def _compute_permittivity(self):
        # 这里+2的原因：稍微扩大一点矩阵的大小，可以保证水平和竖直方向最边上的点不被丢出
        z = x = np.linspace(1, 2 * self.outer_radius + 2, 2 * self.outer_radius + 2)
        Z, X = np.meshgrid(z, x, indexing="ij")  # indexing = 'ij'很重要

        m = (Z - self.outer_radius - 1) ** 2 + (X - self.outer_radius - 1) ** 2 >= (self.outer_radius - self.width) ** 2
        m1 = (Z - self.outer_radius - 1) ** 2 + (X - self.outer_radius - 1) ** 2 <= self.outer_radius ** 2
        m = m == m1
        # 以中心点为圆心创建角度矩阵
        radient_matrix = np.arctan2((X - self.outer_radius - 1), (Z - self.outer_radius - 1))
        # 将负角度变为正角度
        radient_matrix[radient_matrix < 0] = 2 * np.pi + radient_matrix[radient_matrix < 0]

        m2 = radient_matrix >= self.phi
        m3 = radient_matrix <= (self.phi + self.psi) % (2 * np.pi)
        if (self.phi + self.psi) // (2 * np.pi) == 0:
            m = (m2 == m3) & m
        else:
            m = (m2 + m3) & m
        # for i in range(2 * self.outer_radius + 2):
        #     for j in range(2 * self.outer_radius + 2):
        #         if m1[i, j] != m[i, j] or m2[i, j] != m[i, j] or m3[i, j] != m[i, j]:
        #             m[i, j] = 0

        def remove_zero_rows_columns(matrix):
            # 删除矩阵所有元素都为0的行和列
            # 检查每行是否至少有一个非零元素
            non_zero_rows = np.any(matrix != 0, axis=1)

            # 检查每列是否至少有一个非零元素
            non_zero_columns = np.any(matrix != 0, axis=0)

            # 使用布尔掩码筛选原始矩阵
            result_matrix = matrix[non_zero_rows][:, non_zero_columns]

            row_indices, col_indices = np.where(non_zero_rows), np.where(non_zero_columns)

            return result_matrix, row_indices, col_indices

        m_removed, row_indices, col_indices = remove_zero_rows_columns(m)
        try:
            self.z += row_indices[0][0] - self.outer_radius
            self.x += col_indices[0][0] - self.outer_radius
        except:
            self.z += row_indices[0] - self.outer_radius
            self.x += col_indices[0] - self.outer_radius

        m_removed = m_removed.astype(float)
        m_removed[m_removed == 1] *= self.refractive_index ** 2
        m_removed[m_removed == 0] = self.background_index ** 2
        self.zlength = np.shape(m_removed)[0]
        self.xlength = np.shape(m_removed)[1]

        m_broadcast = np.empty((self.xlength, 1, self.zlength))
        m_broadcast[:,0,:] = m_removed[:, :].T
        self.permittivity = np.ones((self.xlength, self.ylength, self.zlength))
        self.permittivity *= m_broadcast
        if self.grid.background_index != 1:
            self.permittivity[self.permittivity == 1] = self.grid.background_index
        pass



