import numpy as np
from .fiber import Fiber
class HC_ARF:
    """
    单层空芯反谐振光纤

    x, y, z: 中心坐标
    N: 毛细管个数
    D: 光纤纤芯直径
    d: 毛细管直径
    t: 毛细管壁厚
    refractive_index: 包层折射率
    axis: 'x', 'y', 'z' 光纤沿哪个轴
    """
    def __init__(self,
                 x: int or float = None,
                 y: int or float = None,
                 z: int or float = None,
                 N: int = None,
                 D: int or float = None,
                 d: int or float = None,
                 t: int or float = None,
                 refractive_index: float = None,
                 axis: str = "z",
                 name: str = "hc_arf",
                 grid=None,
                 priority: int = 1) -> None:

        # 自动选择仿真区域中心
        self.x = x if x is not None else int(grid._grid_xlength / 2)
        self.y = y if y is not None else int(grid._grid_ylength / 2)
        self.z = z if z is not None else int(grid._grid_zlength / 2)

        self.N = N
        self.D = D
        self.d = d
        self.t = t
        self.refractive_index = refractive_index
        self.axis = axis
        self.grid = grid
        self.priority = priority
        self.name = name
        self.fiber_inner = []
        self._internal_objects = []  # 定义内部对象列表

        # 创建外包层
        self._add_fiber_outer()

        # 创建内包层
        if self.N:
            self._add_fiber_inner()

    def _add_fiber_inner(self):
        """创建内包层对象"""
        for i in range(self.N):
            angle_increment = 2 * np.pi / self.N
            angle = i * angle_increment
            x0, y0, z0 = self.x, self.y, self.z
            r = (self.D + self.d) / 2+self.t  # 计算毛细管的半径

            x1 = x0 + r * np.cos(angle)  # 计算毛细管的 X 坐标
            y1 = y0 + r * np.sin(angle)  # 计算毛细管的 Y 坐标
            z1 = z0  # Z 坐标保持不变

            # 创建光纤对象并添加到 fiber_inner 列表中
            fiber = Fiber(length=1, x=x1, y=y1, z=z1,
                          radius=[self.d / 2, (self.d + self.t) / 2],
                          refractive_index=[1.01, self.refractive_index],
                          name=f"fiber{i+1}", axis=self.axis,
                          grid=self.grid, priority=self.priority)
            self.fiber_inner.append(fiber)

            # 将 fiber 添加到内部对象列表
            self._internal_objects.extend(fiber._internal_objects)

    def _add_fiber_outer(self):
        """创建外包层对象"""
        fiber_outer = Fiber(length=1, x=self.x, y=self.y, z=self.z,
                            radius=[(self.D / 2 + self.d+2*self.t), 62.5e-6],
                            refractive_index=[1.01, self.refractive_index],
                            name='fiber_outer', axis=self.axis,
                            grid=self.grid, priority=self.priority)

        # 将外包层光纤添加到内部对象列表
        self._internal_objects.extend(fiber_outer._internal_objects)
