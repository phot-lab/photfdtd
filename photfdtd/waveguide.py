import numpy as np
import fdtd
import matplotlib.pyplot as plt


class Waveguide:
    """
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    width：波导宽度(在矩形波导中，波导宽度没有意义)
    refractive_index:折射率
    name:名称
    ！！！x，y仍然对应FDTD包中的x，y轴！！！
    """

    def __init__(
        self,
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        width=10,
        name="waveguide",
        refractive_index=1.7,
    ):

        self.xlength = xlength
        self.ylength = ylength
        self.zlength = zlength
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.name = name
        self.refractive_index = refractive_index

        self._grid = None  # 用来存储 fdtd.Grid 对象

        self._compute_permittivity()

    def _compute_permittivity(self):
        """矩形波导"""
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
        permittivity += self.refractive_index**2

        self.permittivity = permittivity

    def set_grid(
        self, grid_xlength=100, grid_ylength=200, grid_zlength=50, grid_spacing=0.01, total_time=1, pml_width=10
    ):
        """
        Args:
            grid_xlength (int, optional): _description_. Defaults to 100.
            grid_ylength (int, optional): _description_. Defaults to 200.
            grid_zlength (int, optional): _description_. Defaults to 50.
            grid_spacing (float, optional): fdtd算法的空间步长（yee元胞的网格宽度）. Defaults to 0.01.
            total_time (int, optional): 计算时间. Defaults to 1.
            pml_width (int, optional): PML宽度. Defaults to 10.
        """

        grid = fdtd.Grid(shape=(grid_xlength, grid_ylength, grid_zlength), grid_spacing=grid_spacing)
        if grid_zlength != 1:
            grid[
                self.x : self.x + self.xlength,
                self.y : self.y + self.ylength,
                self.z : self.z + self.zlength,
            ] = fdtd.Object(permittivity=self.permittivity, name=self.name)
        else:
            grid[
                self.x : self.x + self.xlength,
                self.y : self.y + self.ylength,
            ] = fdtd.Object(permittivity=self.permittivity, name=self.name)

        grid[0:pml_width, :, :] = fdtd.PML(name="pml_xlow")
        grid[-pml_width:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:pml_width, :] = fdtd.PML(name="pml_ylow")
        grid[:, -pml_width:, :] = fdtd.PML(name="pml_yhigh")

        if grid_zlength != 1:
            grid[:, :, 0:pml_width] = fdtd.PML(name="pml_zlow")
            grid[:, :, -pml_width:] = fdtd.PML(name="pml_zhigh")

        self._total_time = total_time
        self._grid = grid

    def savefig(self, filepath, axis="x"):
        self._grid.run(total_time=self._total_time)

        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")

        axis = axis.lower()  # 识别大写的 "X"

        if axis == "x":  # 判断从哪一个轴俯视画图
            self._grid.visualize(x=0)
        elif axis == "y":
            self._grid.visualize(y=0)
        elif axis == "z":
            self._grid.visualize(z=0)
        else:
            raise RuntimeError("Unknown axis parameter.")

        plt.savefig(filepath)  # 保存图片
        plt.close()  # 清除画布
