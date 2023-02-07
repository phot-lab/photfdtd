from waveguide import Waveguide
import numpy as np
import fdtd


class Sbend(Waveguide):

    """s波导代码，继承自waveguide
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    flag：=1表示形状左上至右下，=-1表示形状从左下到右上
    width：波导宽度
    refractive_index:折射率"""

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
        flag=-1,
    ):
        super().__init__(xlength, ylength, zlength, x, y, z, width, name, refractive_index)
        self.flag = flag

    def set_grid(self):
        """
        输入波导规格，返回字典，包含名字、介电常数矩阵（规格为[ylength,xlength,zlength]）、区域规格、位置坐标、flag(=1表示形状左上至右下，=-1表示形状从左下到右上)
        """
        x = np.linspace(0, self.xlength, self.xlength)
        y = np.linspace(0, self.ylength, self.ylength)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要
        m = np.zeros((self.xlength, self.ylength, self.zlength))

        if self.flag == 1:
            # flag=1, 波导方向从左上到右下

            m1 = (
                Y
                <= 0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                + self.width / 2
                + self.ylength / 2
            )

            m2 = (
                Y
                >= 0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                - self.width / 2
                + self.ylength / 2
            )

        if self.flag == -1:
            # flag=-1, 波导方向从左下到右上
            m1 = (
                Y
                <= -0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                + self.width / 2
                + self.ylength / 2
            )
            m2 = (
                Y
                >= -0.5 * (self.ylength - self.width) * np.sin((X / self.xlength - 0.5) * np.pi)
                - self.width / 2
                + self.ylength / 2
            )

        for i in range(self.xlength):
            for j in range(self.ylength):
                if m1[i, j] == m2[i, j]:
                    m[i, j, :] = True

        permittivity = np.ones((self.xlength, self.ylength, self.zlength))
        permittivity += m[:, :] * (self.refractive_index**2 - 1)

        result = {
            "name": self.name,
            "permittivity": permittivity,
            "size": (self.xlength, self.ylength, self.zlength),
            "position": (self.x, self.y, self.z),
            "flag": self.flag,
        }

        return result


if __name__ == "__main__":
    sbend = Sbend(
        xlength=40, ylength=60, zlength=1, x=10, y=10, z=1, flag=-1, width=10, refractive_index=1.7, name="sbend"
    )
    result = sbend.set_grid()
    # print(result['size'][0])

    grid = fdtd.Grid(shape=(80, 80, 1), grid_spacing=155e-9)

    grid[
        result["position"][0] : result["position"][0] + result["size"][0],
        result["position"][1] : result["position"][1] + result["size"][1],
    ] = fdtd.Object(permittivity=result["permittivity"], name=result["name"])

    PML_width = 5

    grid[0:PML_width, :, :] = fdtd.PML(name="pml_xlow")
    grid[-PML_width:, :, :] = fdtd.PML(name="pml_xhigh")
    grid[:, 0:PML_width, :] = fdtd.PML(name="pml_ylow")
    grid[:, -PML_width:, :] = fdtd.PML(name="pml_yhigh")

    if sbend.flag == 1:
        grid[11:11, result["position"][1] : result["position"][1] + 10] = fdtd.LineSource(
            period=1550e-9 / 299792458, name="source"
        )
    else:
        grid[
            11 + result["size"][0] : 11 + result["size"][0], result["position"][1] : result["position"][1] + 10
        ] = fdtd.LineSource(period=1550e-9 / 299792458, name="source")

    # grid[55:55, 28:28] = fdtd.PointSource(
    # period=5.16e-15, name="sourced")

    grid.run(total_time=200)
    grid.visualize(z=0, show=True)
