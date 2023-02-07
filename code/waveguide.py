import numpy as np
import fdtd
import matplotlib.pyplot as plt


class Waveguide:
    """
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    flag：参数
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

        self._grid = None

    def set_grid(self, grid_ylength=200, grid_xlength=100, grid_zlength=50, grid_spacing=0.01, total_time=1):

        """矩形波导"""
        permittivity = np.zeros((self.xlength, self.ylength, self.zlength))
        permittivity += self.refractive_index**2

        grid = fdtd.Grid(shape=(grid_ylength, grid_xlength, grid_zlength), grid_spacing=grid_spacing)
        grid[
            self.x : self.x + self.xlength,
            self.y : self.y + self.ylength,
            self.z : self.z + self.zlength,
        ] = fdtd.Object(permittivity=permittivity, name=self.name)

        grid[0:10, :, :] = fdtd.PML(name="pml_xlow")
        grid[-10:, :, :] = fdtd.PML(name="pml_xhigh")
        grid[:, 0:5, :] = fdtd.PML(name="pml_ylow")
        grid[:, -5:, :] = fdtd.PML(name="pml_yhigh")
        grid[:, :, 0:2] = fdtd.PML(name="pml_zlow")
        grid[:, :, -2:] = fdtd.PML(name="pml_zhigh")

        grid.run(total_time=total_time)

        self._grid = grid

    def savefig(self, folder, filename, axis="x"):
        if self._grid is None:
            raise RuntimeError("The grid should be set before saving figure.")

        axis = axis.lower()  # 识别大写的 "X"

        if axis == "x":  # 判断从哪一个轴俯视画图
            self._grid.visualize(x=0, save=True, index=filename, folder=folder)
        elif axis == "y":
            self._grid.visualize(y=0, save=True, index=filename, folder=folder)
        elif axis == "z":
            self._grid.visualize(z=0, save=True, index=filename, folder=folder)
        else:
            raise RuntimeError("Unknown axis parameter.")

        plt.close()  # 清除画布


if __name__ == "__main__":

    # 设置器件参数
    waveguide = Waveguide(
        xlength=40, ylength=20, zlength=10, x=20, y=40, z=5, width=10, refractive_index=1.7, name="Waveguide"
    )

    # 设置 grid 参数
    waveguide.set_grid(grid_ylength=200, grid_xlength=100, grid_zlength=50, grid_spacing=0.01, total_time=1)

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图（这里画了三张图）
    waveguide.savefig(folder="./figures", filename="WaveguideX", axis="x")
    waveguide.savefig(folder="./figures", filename="WaveguideY", axis="y")
    waveguide.savefig(folder="./figures", filename="WaveguideZ", axis="z")
