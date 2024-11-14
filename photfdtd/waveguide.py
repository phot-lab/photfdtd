import numpy as np
from copy import copy


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
    priority: the priority of the waveguide( high index indicates high priority)
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
            material: str = None,
            reset_xyz: bool = True,
            grid=None,
            priority: int = 1
    ) -> None:
        if x == None:
            # If x not set, choose the center of grid. 如果没设置x，自动选仿真区域中心
            x = int(grid._grid_xlength / 2)
        if y == None:
            y = int(grid._grid_ylength / 2)
        if z == None:
            z = int(grid._grid_zlength / 2)

        xlength, x, = grid._handle_unit([xlength, x], grid_spacing=grid._grid.grid_spacing_x)
        ylength, y, = grid._handle_unit([ylength, y], grid_spacing=grid._grid.grid_spacing_y)
        zlength, z, = grid._handle_unit([zlength, z], grid_spacing=grid._grid.grid_spacing_z)
        width = grid._handle_unit([width], grid_spacing=grid._grid.grid_spacing)[0]
        self.xlength = xlength
        self.ylength = ylength
        self.zlength = zlength

        # save the center position保存中心
        self.x_center = copy(x)
        self.y_center = copy(y)
        self.z_center = copy(z)

        if reset_xyz:
            self.x = self.x_center - int(xlength / 2)
            self.y = self.y_center - int(ylength / 2)
            self.z = self.z_center - int(zlength / 2)
        else:
            self.x = copy(x)
            self.y = copy(y)
            self.z = copy(z)

        if not width:
            self.width = self.xlength
        else:
            self.width = width
        self.name = name
        self.refractive_index = refractive_index
        self.background_index = grid.background_index

        self.grid = grid

        self.priority = priority

        self._compute_permittivity()
        self._set_objects()
        self._compute_priority()

    def _compute_permittivity(self):
        """计算介电常数矩阵"""
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
        permittivity += self.refractive_index ** 2

        self.permittivity = permittivity

    def _compute_priority(self):
        # the priority matrix of the waveguide
        if hasattr(self, "permittivity"):
            self.priority_matrix = (self.permittivity == self.refractive_index ** 2) * self.priority
        for obj in self._internal_objects:
            if hasattr(obj, "permittivity"):
                obj.priority_matrix = (obj.permittivity == obj.refractive_index ** 2) * obj.priority

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

    def rotate_X(self, angle: float = None, center: list = None, angle_unit: bool = True):
        self._rotate_(angle, center, angle_unit, "x")
        self._compute_priority()

    def rotate_Y(self, angle: float = None, center: list = None, angle_unit: bool = True):
        self._rotate_(angle, center, angle_unit, "y")
        self._compute_priority()

    def rotate_Z(self, angle: float = None, center: list = None, angle_unit: bool = True):
        self._rotate_(angle, center, angle_unit, "z")
        self._compute_priority()

    def _rotate_(self, angle: float = None, center: list = None, angle_unit: bool = True, axis: str = None):
        """
        # TODO: 这个函数可以用。但也许在矩阵中描点连线也可以？
        Rotate a waveguide around the z-axis on x-y plane
        @param angle_unit: bool, default to True. False if using radian unit
        @param angle: Angle of rotation with respect to the positive direction of the x-axis
        @param center: Center position of rotation (on simulation region coordinate), if not given, it will be the center of waveguide.
        """
        # 分清楚以仿真区域坐标系、center坐标系和波导原点坐标系
        if not angle:
            pass
        matrix = self.permittivity
        shape = matrix.shape
        if center:
            center[0] = self.grid._handle_unit(center[0], grid_spacing=self.grid._grid.grid_spacing_x)[0]
            center[1] = self.grid._handle_unit(center[1], grid_spacing=self.grid._grid.grid_spacing_y)[0]
            center[2] = self.grid._handle_unit(center[2], grid_spacing=self.grid._grid.grid_spacing_z)[0]
            center = [center[0] - self.x, center[1] - self.y, center[2] - self.z]
        elif center is None:
            # 这里的center是波导原点坐标系，输入的center也是
            center = np.array([shape[0] // 2, shape[1] // 2, shape[2] // 2])

        # 角度转弧度
        if angle_unit:
            angle = np.radians(angle)

        # Rotation matrix 创建绕 z 轴的旋转矩阵
        if axis == "z":
            rotation_matrix = np.array([[np.cos(angle), -np.sin(angle), 0],
                                        [np.sin(angle), np.cos(angle), 0],
                                        [0, 0, 1]])
        elif axis == "y":
            rotation_matrix = np.array([[np.cos(angle), 0, -np.sin(angle)],
                                        [0, 1, 0],
                                        [np.sin(angle), 0, np.cos(angle)]])
        elif axis == "x":
            rotation_matrix = np.array([[1, 0, 0],
                                        [0, np.cos(angle), -np.sin(angle)],
                                        [0, np.sin(angle), np.cos(angle)]])
        else:
            raise ValueError("Parameter 'axis' need to be set")
        # Coordinates relative to center相对坐标 center坐标系
        relative_coords = np.array(np.meshgrid(range(shape[0]), range(shape[1]), range(shape[2]))).T.reshape(-1, 3)
        relative_coords -= center

        # Rotate  rotated_coords也是center坐标系
        rotated_coords = np.empty_like(relative_coords)
        for i in range(relative_coords.shape[0]):
            rotated_coords[i] = rotation_matrix @ relative_coords[i]
        #
        # []内应该是center坐标系下center的坐标, 这一步代码完成后center_changed是
        # center 旋转之后在center坐标系下的新坐标
        center_changed = rotation_matrix @ [self.x_center - self.x - center[0], self.y_center - self.y - center[1],
                                            self.z_center - self.z - center[2]]
        #  center_changed现在成为了center的变化量，与center无关,
        center_changed -= [self.x_center - self.x - center[0], self.y_center - self.y - center[1],
                           self.z_center - self.z - center[2]]

        # Note the min indexes and make the min coordinate equals 0
        self.x_changed, self.y_changed, self.z_changed = min(rotated_coords[:, 0]), min(rotated_coords[:, 1]), min(
            rotated_coords[:, 2])

        rotated_coords[:, 0] -= self.x_changed
        rotated_coords[:, 1] -= self.y_changed
        rotated_coords[:, 2] -= self.z_changed

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
                    if rotated_matrix[i, j, k] == 0:
                        # if all([rotated_matrix[i - 1, j, k] != 0, rotated_matrix[i + 1, j, k] != 0,
                        #         rotated_matrix[i, j - 1, k] != 0, rotated_matrix[i, j + 1, k] != 0]):
                        #     rotated_matrix[i, j, k] += (rotated_matrix[i - 1, j, k] + rotated_matrix[i + 1, j, k] +
                        #                                 rotated_matrix[i, j - 1, k]
                        #                                 + rotated_matrix[i, j + 1, k]) / 4
                        if i + 1 < rotated_matrix.shape[0] and all(
                                [rotated_matrix[i - 1, j, k] != 0, rotated_matrix[i + 1, j, k] != 0]):
                            rotated_matrix[i, j, k] += (rotated_matrix[i - 1, j, k] + rotated_matrix[
                                i + 1, j, k]) / 2
                        elif j + 1 < rotated_matrix.shape[1] and all(
                                [rotated_matrix[i, j - 1, k] != 0, rotated_matrix[i, j + 1, k] != 0]):
                            rotated_matrix[i, j, k] += (rotated_matrix[i, j - 1, k] + rotated_matrix[
                                i, j + 1, k]) / 2
                        elif k + 1 < rotated_matrix.shape[2] and all(
                                [rotated_matrix[i, j, k - 1] != 0, rotated_matrix[i, j, k + 1] != 0]):
                            rotated_matrix[i, j, k] += (rotated_matrix[i, j, k - 1] + rotated_matrix[
                                i, j, k + 1]) / 2
        # remove all-zero slices to reduce matrix's size
        rotated_matrix = self.remove_zero_slices(rotated_matrix)
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
