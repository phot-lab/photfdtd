from waveguide import Waveguide
import sbend
import fdtd

# import os


class DirectionalCoupler(Waveguide):
    """方向耦合器，返回两个s波导的介电常数矩阵
    xlength: 波导区域x方向宽度
    ylength: 波导区域y方向宽度
    zlength: 波导区域z方向宽度，通常也是波导高度
    x,y,z: 波导位置坐标（通常是矩形区域最靠近原点的点）
    flag：参数
    width：波导宽度
    refractive_index:折射率
    gap:直波导间距
    xlength_rectangle：直波导长度(耦合长度)"""

    # TODO 只需要输出两个s波导的矩阵，另外两个S波导的矩阵与他们一样，关键在于确定位置（未完成）
    def __init__(
        self,
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        flag=1,
        width=10,
        name="waveguide",
        refractive_index=1.7,
        xlength_rectangle=30,
        gap=5,
    ):
        Waveguide.__init__(self, xlength, ylength, zlength, x, y, z, flag, width, name, refractive_index)
        self.xlength_rectangle = xlength_rectangle
        self.ylength_sbend = int((ylength - gap) / 2 + 0.5)
        self.xlength_sbend = int((xlength - xlength_rectangle) / 2 + 0.5)
        self.gap = gap

    def set_grid(self):
        # permittivity_rectangle = 应该不用写矩形波导的介电常数？
        # 左上波导sbend1
        sbend1 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            flag=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="DC_sbend1",
        )
        # 左下波导sbend2
        sbend2 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend + self.xlength_rectangle,
            y=self.y,
            z=self.z,
            flag=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="DC_sbend2",
        )

        # 右上波导sbend3
        sbend3 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x,
            y=self.y + self.ylength_sbend + self.gap,
            z=self.z,
            flag=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="DC_sbend3",
        )

        # 右下波导sbend4
        sbend4 = sbend.Sbend(
            xlength=self.xlength_sbend,
            ylength=self.ylength_sbend,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend + self.xlength_rectangle,
            y=self.y + self.ylength_sbend + self.gap,
            z=self.z,
            flag=1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="DC_sbend4",
        )

        wg1 = Waveguide(
            xlength=self.xlength_rectangle,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend,
            y=self.y + self.ylength_sbend - self.width,
            z=self.z,
            flag=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="DC_wg1",
        )

        wg2 = Waveguide(
            xlength=self.xlength_rectangle,
            ylength=self.width,
            zlength=self.zlength,
            x=self.x + self.xlength_sbend,
            y=self.y + self.ylength_sbend + self.gap,
            z=self.z,
            flag=-1,
            width=self.width,
            refractive_index=self.refractive_index,
            name="DC_wg2",
        )

        # result_sbend1 = sbend1.set_grid()
        # result_sbend2 = sbend2.set_grid()
        # result_sbend3 = sbend3.set_grid()
        # result_sbend4 = sbend4.set_grid()
        # result_wg1 = wg1.set_grid()
        # result_wg2 = wg2.set_grid()

        result = (
            sbend1.set_grid(),
            sbend2.set_grid(),
            sbend3.set_grid(),
            sbend4.set_grid(),
            wg1.set_grid(),
            wg2.set_grid(),
        )

        return result


if __name__ == "__main__":
    dc = DirectionalCoupler(
        xlength=150,
        ylength=65,
        zlength=1,
        x=20,
        y=20,
        z=20,
        flag=1,
        width=4,
        name="dc",
        refractive_index=3.47,
        xlength_rectangle=60,
        gap=1,
    )
    result = dc.set_grid()
    # print(p1, p2)

    grid = fdtd.Grid(shape=(175, 120, 1), grid_spacing=155e-9, permittivity=1**2)

    for i in range(6):
        grid[
            result[i]["position"][0] : result[i]["position"][0] + result[i]["size"][0],
            result[i]["position"][1] : result[i]["position"][1] + result[i]["size"][1],
        ] = fdtd.Object(permittivity=result[i]["permittivity"], name=result[i]["name"])

    PML_width = 5

    grid[0:PML_width, :, :] = fdtd.PML(name="pml_xlow")
    grid[-PML_width:, :, :] = fdtd.PML(name="pml_xhigh")
    grid[:, 0:PML_width, :] = fdtd.PML(name="pml_ylow")
    grid[:, -PML_width:, :] = fdtd.PML(name="pml_yhigh")

    grid[10:10, result[0]["position"][1] : result[0]["position"][1] + dc.width] = fdtd.LineSource(
        period=1550e-9 / 299792458, name="source", pulse=True
    )
    # grid[10:10, 10:110] = fdtd.LineSource(
    #     period=1550e-9 / 299792458, name="source")

    # grid[55:55, 28:28] = fdtd.PointSource(
    # period=5.16e-15, name="sourced")

    # grid[10:110, 10:110, 0] = fdtd.BlockDetector(name="detector")

    # simfolder = grid.save_simulation("dc")  # initializing environment to save simulation data

    # with open(os.path.join(simfolder, "grid.txt"), "w") as f:
    #     f.write(str(grid))
    #     wavelength = 1550e-9
    #     wavelengthUnits = wavelength/grid.grid_spacing
    #     GD = np.array([grid.x, grid.y, grid.z])
    #     gridRange = [np.arange(x/grid.grid_spacing) for x in GD]
    #     objectRange = np.array([[gridRange[0][x.x], gridRange[1][x.y], gridRange[2][x.z]] for x in grid.objects], dtype=object).T
    #     f.write("\n\nGrid details (in wavelength scale):")
    #     f.write("\n\tGrid dimensions: ")
    #     f.write(str(GD/wavelength))
    #     # f.write("\n\tSource dimensions: ")
    #     # f.write(str(np.array([grid.source.x[-1] - grid.source.x[0] + 1, grid.source.y[-1] - grid.source.y[0] + 1, grid.source.z[-1] - grid.source.z[0] + 1])/wavelengthUnits))
    #     f.write("\n\tObject dimensions: ")
    #     f.write(str([(max(map(max, x)) - min(map(min, x)) + 1)/wavelengthUnits for x in objectRange]))

    grid.run(total_time=1000)
    # grid.save_data()

    # df = np.load(os.path.join(simfolder, "detector_readings.npz"))
    # fdtd.dB_map_2D(df["detector (E)"])
    grid.visualize(z=0, show=True)
