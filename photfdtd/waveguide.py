import numpy as np


# from .grid import Grid

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
            xlength: int or float = 200,
            ylength: int or float = 20,
            zlength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width: int or float = None,
            name: str = "waveguide",
            refractive_index: float = None,
            material: str = "",
            reset_xyz: bool = True,
            grid=None
    ) -> None:
        if x == None:
            # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
            x = int(grid._grid_xlength / 2)
        if y == None:
            y = int(grid._grid_ylength / 2)
        if z == None:
            z = int(grid._grid_zlength / 2)

        xlength, ylength, zlength, width, x, y, z = grid._handle_unit([xlength, ylength, zlength, width, x, y, z],
                                                                      grid_spacing=grid._grid.grid_spacing)

        self.xlength = xlength
        self.ylength = ylength
        self.zlength = zlength

        if reset_xyz:
            self.x = x - int(xlength / 2)
            self.y = y - int(ylength / 2)
            self.z = z - int(zlength / 2)
        else:
            self.x = x
            self.y = y
            self.z = z
        self.width = width
        self.name = name
        self.refractive_index = refractive_index
        self.background_index = grid.background_index

        # save the center position保存中心
        self.x_center = x
        self.y_center = y
        self.z_center = z

        self.grid = grid

        self._compute_permittivity()
        self._set_objects()

    def _compute_permittivity(self):
        """计算介电常数矩阵"""
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
        permittivity += self.refractive_index ** 2

        self.permittivity = permittivity

    def _set_objects(self):
        self._internal_objects = [self]

    @staticmethod
    def remove_zero_slices(matrix):
        # Delete all-zero 2D slices, xx, yy, zz represents the new matrix's position in the original matrix
        shape = matrix.shape
        if len(shape) == 2:

            non_zero_rows = np.any(matrix != 0, axis=1)
            non_zero_columns = np.any(matrix != 0, axis=0)
            # 使用布尔掩码筛选原始矩阵
            matrix = matrix[non_zero_rows][:, non_zero_columns]
            xx_position, yy_position = np.where(non_zero_rows), np.where(non_zero_columns)

            zz_position = [0]

        else:

            zero_slices_x = np.where(np.all(matrix == 0, axis=(1, 2)))
            zero_slices_y = np.where(np.all(matrix == 0, axis=(0, 2)))
            zero_slices_z = np.where(np.all(matrix == 0, axis=(0, 1)))

            matrix = np.delete(matrix, zero_slices_x, axis=0)
            matrix = np.delete(matrix, zero_slices_y, axis=1)
            matrix = np.delete(matrix, zero_slices_z, axis=2)
            xx_position = np.delete(np.arange(shape[0]), zero_slices_x)
            yy_position = np.delete(np.arange(shape[1]), zero_slices_y)
            zz_position = np.delete(np.arange(shape[2]), zero_slices_z)

        return matrix, xx_position, yy_position, zz_position

    def rotate_Z(self, angle, center=None, angle_to_radian: bool = True):
        """
        # TODO: 这个函数的效果没有想象的那么好。也许还是应该在矩阵中描点连线更方便？
        Rotate a waveguide around the z-axis
        @param angle: Angle of rotation with respect to the positive direction of the x-axis
        @param center: Center of rotation, if not given, it will be the center of waveguide.
        """
        # 分清楚以仿真区域坐标系、center坐标系和波导原点坐标系
        # matrix_size = int(np.sqrt((self.xlength / 2) ** 2 + (self.ylength / 2) ** 2)) * 2 + 2
        # # 计算在每个维度上需要填充的数量
        # # np.ceil(0.1) = 1.0（向上取整）
        # pad_x = int(np.ceil((matrix_size - self.permittivity.shape[0]) // 2))
        # pad_y = int(np.ceil((matrix_size - self.permittivity.shape[1]) // 2))
        #
        # # 使用 np.pad 在矩阵周围添加0
        # matrix = np.pad(self.permittivity, ((pad_x, pad_x), (pad_y, pad_y), (0, 0)), mode='constant',
        #                 constant_values=0)
        if angle == 0:
            pass
        matrix = self.permittivity
        shape = matrix.shape
        if center is None:
            # 这里的center是波导原点坐标系，输入的center也是
            center = np.array([shape[0] // 2, shape[1] // 2, shape[2] // 2])

        # 角度转弧度
        if angle_to_radian:
            angle = np.radians(angle)

        # Rotation matrix 创建绕 z 轴的旋转矩阵
        rotation_z = np.array([[np.cos(angle), -np.sin(angle), 0],
                               [np.sin(angle), np.cos(angle), 0],
                               [0, 0, 1]])

        # Coordinates relative to center相对坐标 center坐标系
        relative_coords = np.array(np.meshgrid(range(shape[0]), range(shape[1]), range(shape[2]))).T.reshape(-1, 3)
        relative_coords -= center

        # Rotate  rotated_coords也是center坐标系
        rotated_coords = np.empty_like(relative_coords)
        for i in range(relative_coords.shape[0]):
            rotated_coords[i] = rotation_z @ relative_coords[i]
        #
        # []内应该是center坐标系下center的坐标, 这一步代码完成后center_changed是
        # center 旋转之后在center坐标系下的新坐标
        center_changed = rotation_z @ [self.x_center - self.x - center[0], self.y_center - self.y - center[1],
                                       self.z_center - self.z - center[2]]
        #  center_changed现在成为了center的变化量，与center无关,
        center_changed -= [self.x_center - self.x - center[0], self.y_center - self.y - center[1],
                           self.z_center - self.z - center[2]]

        # Note the min indexes and make the min coordinate equals 0
        self.x_changed, self.y_changed, self.z_changed = min(rotated_coords[:, 0]), min(rotated_coords[:, 1]), min(
            rotated_coords[:, 2])

        # xx = self.x_changed - self.x_center
        # yy = self.y_changed - self.y_center
        # zz = self.z_changed - self.z_center

        rotated_coords[:, 0] -= self.x_changed
        rotated_coords[:, 1] -= self.y_changed
        rotated_coords[:, 2] -= self.z_changed

        # self.x_changed += center[0]
        # self.y_changed += center[1]
        # self.z_changed += center[2]

        # rotated_coords += center
        # Restore to absolute coordinates将坐标还原为绝对坐标
        relative_coords += center

        # Mapping the rotated coordinates according to the original matrix 将旋转后的坐标映射到新矩阵
        rotated_matrix = np.zeros(
            [max(abs(rotated_coords[:, 0])) + 1, max(abs(rotated_coords[:, 1])) + 1,
             max(abs(rotated_coords[:, 2])) + 1],
            dtype=matrix.dtype)
        for i in range(len(rotated_coords)):
            x, y, z = rotated_coords[i]
            rotated_matrix[x, y, z] = matrix[relative_coords[i, 0], relative_coords[i, 1], relative_coords[i, 2]]
        # Fill the blank holes
        for i in range(rotated_matrix.shape[0]):
            for j in range(rotated_matrix.shape[1]):
                for k in range(rotated_matrix.shape[2]):
                    if i + 1 < rotated_matrix.shape[0] and j + 1 < rotated_matrix.shape[1]:
                        # if rotated_matrix[i,j,k] != 0 and all(
                        #         [rotated_matrix[i - 1, j, k] == 0, rotated_matrix[i + 1, j, k] == 0,
                        #          rotated_matrix[i, j - 1, k] == 0, rotated_matrix[i, j + 1, k] == 0]):
                        #     rotated_matrix[i, j, k] = 0
                        if rotated_matrix[i, j, k] == 0 and all(
                                [rotated_matrix[i - 1, j, k] != 0, rotated_matrix[i + 1, j, k] != 0,
                                 rotated_matrix[i, j - 1, k] != 0, rotated_matrix[i, j + 1, k] != 0]):
                            rotated_matrix[i, j, k] += (rotated_matrix[i - 1, j, k] + rotated_matrix[i + 1, j, k] +
                                                        rotated_matrix[i, j - 1, k]
                                                        + rotated_matrix[i, j + 1, k]) / 4
                        # if i + 1 < rotated_matrix.shape[0] and j + 1 < rotated_matrix.shape[1]:
                        #     flag = 0
                        #     if rotated_matrix[i - 1, j, k] != 0:
                        #         flag += 1
                        #     if rotated_matrix[i + 1, j, k] != 0:
                        #         flag += 1
                        #     if rotated_matrix[i, j-1, k] != 0:
                        #         flag += 1
                        #     if rotated_matrix[i, j+1, k] != 0:
                        #         flag += 1
                        #     if flag >= 2:
                        #         rotated_matrix[i, j, k] = self.refractive_index ** 2

        # for i in range(rotated_matrix.shape[0]):
        #     for j in range(rotated_matrix.shape[1]):
        #         for k in range(rotated_matrix.shape[2]):
        #             if i + 1 < rotated_matrix.shape[0] and j + 1 < rotated_matrix.shape[1]:
        #                 # flag = np.sum(bool([rotated_matrix[i - 1, j, k], rotated_matrix[i + 1, j, k],
        #                 #         rotated_matrix[i, j - 1, k], rotated_matrix[i, j + 1, k]]))
        #                 if all([rotated_matrix[i - 1, j, k] == 0, rotated_matrix[i + 1, j, k] == 0,
        #                         rotated_matrix[i, j - 1, k] == 0, rotated_matrix[i, j + 1, k] == 0]):
        #                     rotated_matrix[i, j, k] = 0

        # Remove all-zero slices
        # rotated_matrix, self.xx, self.yy, self.zz = self.remove_zero_slices(rotated_matrix)
        rotated_matrix = self.remove_zero_slices(rotated_matrix)
        # self.x_changed += rotated_matrix[1][0]
        # self.y_changed += rotated_matrix[2][0]
        # self.z_changed += rotated_matrix[3][0]
        rotated_matrix = rotated_matrix[0]
        rotated_matrix[rotated_matrix == 0] += self.background_index ** 2

        self.permittivity = rotated_matrix

        self.xlength = rotated_matrix.shape[0]
        self.ylength = rotated_matrix.shape[1]
        self.zlength = rotated_matrix.shape[2]

        # self.x_center始终是仿真区域坐标系
        self.x_center += int(center_changed[0])
        self.y_center += int(center_changed[1])
        self.z_center += int(center_changed[2])
        self.x = self.x_center - int(self.xlength / 2)
        self.y = self.y_center - int(self.ylength / 2)
        self.z = self.z_center - int(self.zlength / 2)

    def _rotate(self, angle_x, angle_y, angle_z, center=None):
        pass
        # 创建一个立方体，所有元素初始化为0
        matrix_size = int(np.sqrt((self.xlength / 2) ** 2 + (self.ylength / 2) ** 2 + (self.zlength / 2) ** 2) * 2) + 2

        # 计算在每个维度上需要填充的数量
        # np.ceil(0.1) = 1.0（向上取整）
        pad_m = int(np.ceil((matrix_size - self.permittivity.shape[0]) // 2))
        pad_n = int(np.ceil((matrix_size - self.permittivity.shape[1]) // 2))
        pad_l = int(np.ceil((matrix_size - self.permittivity.shape[2]) // 2))

        # 使用 np.pad 在矩阵周围添加0
        matrix = np.pad(self.permittivity, ((pad_m, pad_m), (pad_n, pad_n), (pad_l, pad_l)), mode='constant',
                        constant_values=0)

        if center is None:
            center = np.array([matrix_size // 2, matrix_size // 2, matrix_size // 2])

        def rotate_3d_matrix(matrix, center, angles):
            # 获取矩阵形状
            shape = matrix.shape

            # 将矩阵坐标转换为相对于中心的坐标
            relative_coords = np.array(np.meshgrid(range(shape[0]), range(shape[1]), range(shape[2]))).T.reshape(-1, 3)
            relative_coords -= center

            # 创建旋转矩阵
            rotation_matrix = np.array([[np.cos(np.radians(angles[0])), -np.sin(np.radians(angles[0])), 0],
                                        [np.sin(np.radians(angles[0])), np.cos(np.radians(angles[0])), 0],
                                        [0, 0, 1]])

            # 应用旋转矩阵
            rotated_coords = np.dot(relative_coords, rotation_matrix.T)

            # 将坐标还原为绝对坐标
            rotated_coords += center

            # 四舍五入到整数坐标
            rotated_coords = np.round(rotated_coords).astype(int)

            # 创建新的矩阵
            rotated_matrix = np.zeros(shape, dtype=matrix.dtype)

            # 将旋转后的坐标映射回原矩阵
            for i in range(len(rotated_coords)):
                x, y, z = rotated_coords[i]
                if 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]:
                    rotated_matrix[x, y, z] = matrix[
                        relative_coords[i, 0], relative_coords[i, 1], relative_coords[i, 2]]

            return rotated_matrix

        # 设置中心点和旋转角度

        # 执行旋转操作
        rotated_matrix = rotate_3d_matrix(matrix, center, [angle_x, angle_y, angle_z])
        rotated_matrix, xx, yy, zz = self.remove_zero_slices(rotated_matrix)
        rotated_matrix *= self.refractive_index ** 2
        rotated_matrix[rotated_matrix == 0] += self.background_index ** 2
        self.permittivity = rotated_matrix
        self.xlength = rotated_matrix.shape[0]
        self.ylength = rotated_matrix.shape[0]
        self.zlength = rotated_matrix.shape[0]
