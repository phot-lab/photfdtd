from waveguide import Waveguide
import numpy as np
import fdtd

# import os


class Ring(Waveguide):
    # TODO: 由于在设置的波导中，非波导部分折射率都为1，因此目前设置空间折射率来改变包层折射率并无意义
    """环形谐振腔，继承自Waveguide
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 位置坐标（通常是矩形区域最靠近原点的点）
    width: 波导宽度
    l: 耦合长度
    gap: 环与直波导间距
    refractive_index:折射率
    name: 名称
    flag: 无意义
    """

    def __init__(
        self,
        outer_radius=60,
        zlength=10,
        x=50,
        y=50,
        z=50,
        width=5,
        l=0,
        gap=2,
        name="ring",
        refractive_index=3.47,
        flag=1,
    ):
        self.outer_r = outer_radius
        self.zlength = zlength
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.name = name
        self.refractive_index = refractive_index
        self.l = l
        self.gap = 0
        self.flag = flag

    def set_ring(self):

        y = np.linspace(1, 2 * self.outer_r, 2 * self.outer_r)
        x = np.linspace(1, 2 * self.outer_r + self.l, 2 * self.outer_r + self.l)
        # TODO：把这个语句改成从1开始？
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要

        if self.l == 0:

            m1 = (self.outer_r - self.width) ** 2 <= (X - self.outer_r) ** 2 + (Y - self.outer_r) ** 2
            m = (X - self.outer_r) ** 2 + (Y - self.outer_r) ** 2 <= self.outer_r**2

        for i in range(2 * self.outer_r + self.l):
            for j in range(2 * self.outer_r):
                if m[i, j] != m1[i, j]:
                    m[i, j] = 0

        else:

            m = np.zeros((self.outer_r * 2 + self.l, self.outer_r * 2, self.zlength))

            for j in range(2 * self.outer_r):
                for i in range(self.outer_r):

                    # 左半圆弧
                    if (self.outer_r - self.width) ** 2 <= (X[i, j] - self.outer_r) ** 2 + (
                        Y[i, j] - self.outer_r
                    ) ** 2 and (X[i, j] - self.outer_r) ** 2 + (Y[i, j] - self.outer_r) ** 2 <= self.outer_r**2:
                        m[i, j] = 1

                    if (self.outer_r - self.width) ** 2 <= (
                        X[self.outer_r + self.l + i, j] - self.outer_r - self.l
                    ) ** 2 + (Y[self.outer_r + self.l + i, j] - self.outer_r) ** 2 and (
                        X[self.outer_r + self.l + i, j] - self.outer_r - self.l
                    ) ** 2 + (
                        Y[self.outer_r + self.l + i, j] - self.outer_r
                    ) ** 2 <= self.outer_r**2:
                        m[self.outer_r + self.l + i, j] = 1

            for i in range(self.l):
                for j in range(self.width):
                    # 直波导
                    m[i + self.outer_r, j] = m1[i + self.outer_r, j] = 1
                    m[i + self.outer_r, 2 * self.outer_r - j - 1] = m1[i + self.outer_r, 2 * self.outer_r - j - 1] = 1

        permittivity = np.ones((self.outer_r * 2 + self.l, self.outer_r * 2, self.zlength))
        permittivity += m[:, :] * (self.refractive_index**2 - 1)

        result = {
            "name": self.name,
            "permittivity": permittivity,
            "size": (self.outer_r * 2 + self.l, self.outer_r * 2, self.zlength),
            "position": (self.x, self.y + self.width + self.gap, self.z),
            "flag": self.flag,
        }

        return result

    def set_wg(self):

        wg_bottom = Waveguide(
            xlength=self.outer_r * 2 + self.l,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            flag=self.flag,
            width=self.width,
            name="waveguide_bottom_%s" % self.name,
            refractive_index=self.refractive_index,
        )

        wg_top = Waveguide(
            xlength=self.outer_r * 2 + self.l,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x,
            y=self.y + self.width + self.gap * 2 + self.outer_r * 2,
            z=self.z,
            flag=self.flag,
            width=self.width,
            name="waveguide_top_%s" % self.name,
            refractive_index=self.refractive_index,
        )

        result_top = wg_top.set_grid()
        result_bottom = wg_bottom.set_grid()

        return result_top, result_bottom


if __name__ == "__main__":

    ring = Ring(
        outer_radius=50,
        zlength=1,
        x=10,
        y=10,
        z=1,
        width=4,
        l=0,
        gap=1,
        name="ring",
        refractive_index=1.7,
        flag=1,
    )
    result_ring = ring.set_ring()
    result_top, result_bottom = ring.set_wg()
    # print(result_ring['name'])

    grid = fdtd.Grid(shape=(120, 130, 1), grid_spacing=155e-9)
    # permittivity=1.44 ** 2)

    grid[
        result_ring["position"][0] : result_ring["position"][0] + result_ring["size"][0],
        result_ring["position"][1] : result_ring["position"][1] + result_ring["size"][1],
    ] = fdtd.Object(permittivity=result_ring["permittivity"], name=result_ring["name"])

    grid[
        result_top["position"][0] : result_top["position"][0] + result_top["size"][0],
        result_top["position"][1] : result_top["position"][1] + result_top["size"][1],
    ] = fdtd.Object(permittivity=result_top["permittivity"], name=result_top["name"])

    grid[
        result_bottom["position"][0] : result_bottom["position"][0] + result_bottom["size"][0],
        result_bottom["position"][1] : result_bottom["position"][1] + result_bottom["size"][1],
    ] = fdtd.Object(permittivity=result_bottom["permittivity"], name=result_bottom["name"])

    PML_width = 5

    grid[0:PML_width, :, :] = fdtd.PML(name="pml_xlow")
    grid[-PML_width:, :, :] = fdtd.PML(name="pml_xhigh")
    grid[:, 0:PML_width, :] = fdtd.PML(name="pml_ylow")
    grid[:, -PML_width:, :] = fdtd.PML(name="pml_yhigh")

    grid[8:8, result_bottom["position"][1] - 1 : result_bottom["position"][1] + 6] = fdtd.LineSource(
        period=1550e-9 / 299792458, name="source"
    )
    # pulse = False,cycle=3, hanning_dt=4e-15)

    # grid[10:110, 10:120, 0] = fdtd.BlockDetector(name="detector")
    #
    # simfolder = grid.save_simulation("ring")  # initializing environment to save simulation data
    #
    # with open(os.path.join(simfolder, "grid.txt"), "w") as f:
    #     f.write(str(grid))
    #     wavelength = 1550e-9
    #     wavelengthUnits = wavelength / grid.grid_spacing
    #     GD = np.array([grid.x, grid.y, grid.z])
    #     gridRange = [np.arange(x / grid.grid_spacing) for x in GD]
    #     objectRange = np.array([[gridRange[0][x.x], gridRange[1][x.y], gridRange[2][x.z]] for x in grid.objects],
    #                            dtype=object).T
    #     f.write("\n\nGrid details (in wavelength scale):")
    #     f.write("\n\tGrid dimensions: ")
    #     f.write(str(GD / wavelength))
    #     # f.write("\n\tSource dimensions: ")
    #     # f.write(str(np.array([grid.source.x[-1] - grid.source.x[0] + 1, grid.source.y[-1] - grid.source.y[0] + 1, grid.source.z[-1] - grid.source.z[0] + 1])/wavelengthUnits))
    #     f.write("\n\tObject dimensions: ")
    #     f.write(str([(max(map(max, x)) - min(map(min, x)) + 1) / wavelengthUnits for x in objectRange]))

    grid.run(total_time=1000)
    # grid.save_data()

    # df = np.load(os.path.join(simfolder, "detector_readings.npz"))
    # fdtd.dB_map_2D(df["detector (E)"])
    grid.visualize(z=0, show=True)
