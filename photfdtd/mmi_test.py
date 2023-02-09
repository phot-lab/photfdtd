from mmi import Mmi
import fdtd

# import os


if __name__ == "__main__":
    n = 1  # 输入端口数
    m = 2  # 输出端口数
    time = 1500
    PML_width = 5
    lambda0 = 1550e-9  # 输入光波长（单位m）
    grid_spacing = 110e-9  # 空间步长

    mmi = Mmi(
        xlength=118,
        ylength=36,
        zlength=1,
        We=37,
        x=50,
        y=10,
        z=1,
        flag=1,
        name="mmi",
        refractive_index=3.47,
        n=n,
        m=m,
        width_port=8,
        width_wg=2,
        l_port=10,
        ln=40,
        lm=5,
    )

    result0 = mmi.set_box()
    result_in, result_out, result_in_wg, result_out_wg = mmi.set_ports()
    grid = fdtd.Grid(
        shape=(mmi.xlength + mmi.ln + mmi.lm + mmi.l_port * 2, mmi.ylength + 2 * PML_width + 10, 1),
        grid_spacing=grid_spacing,
        permittivity=1,
    )

    for i in range(n):
        grid[
            result_in[i]["position"][0] : result_in[i]["position"][0] + result_in[i]["size"][0],
            result_in[i]["position"][1] : result_in[i]["position"][1] + result_in[i]["size"][1],
            :,
        ] = fdtd.Object(permittivity=result_in[i]["permittivity"], name=result_in[i]["name"])

        grid[
            result_in_wg[i]["position"][0] : result_in_wg[i]["position"][0] + result_in_wg[i]["size"][0],
            result_in_wg[i]["position"][1] : result_in_wg[i]["position"][1] + result_in_wg[i]["size"][1],
            :,
        ] = fdtd.Object(permittivity=result_in_wg[i]["permittivity"], name=result_in_wg[i]["name"])

    for i in range(m):
        grid[
            result_out[i]["position"][0] : result_out[i]["position"][0] + result_out[i]["size"][0],
            result_out[i]["position"][1] : result_out[i]["position"][1] + result_out[i]["size"][1],
            :,
        ] = fdtd.Object(permittivity=result_out[i]["permittivity"], name=result_out[i]["name"])

        grid[
            result_out_wg[i]["position"][0] : result_out_wg[i]["position"][0] + result_out_wg[i]["size"][0],
            result_out_wg[i]["position"][1] : result_out_wg[i]["position"][1] + result_out_wg[i]["size"][1],
            :,
        ] = fdtd.Object(permittivity=result_out_wg[i]["permittivity"], name=result_out_wg[i]["name"])

    grid[
        result0["position"][0] : result0["position"][0] + result0["size"][0],
        result0["position"][1] : result0["position"][1] + result0["size"][1],
        :,
    ] = fdtd.Object(permittivity=result0["permittivity"], name=result0["name"])

    grid[0:PML_width, :, :] = fdtd.PML(name="pml_xlow")
    grid[-PML_width:, :, :] = fdtd.PML(name="pml_xhigh")
    grid[:, 0:PML_width, :] = fdtd.PML(name="pml_ylow")
    grid[:, -PML_width:, :] = fdtd.PML(name="pml_yhigh")

    for i in range(n):
        grid[
            9:9, result_in[i]["position"][1] : result_in[i]["position"][1] + result_in[i]["size"][1], :
        ] = fdtd.LineSource(period=1550e-9 / 299792458, name="source%d" % i)

    # grid[result0['position'][0]:result0['position'][0]+result0['size'][0],
    # result0['position'][1]:result0['position'][1]+result0['size'][1], 0] = fdtd.BlockDetector(name="detector")
    #
    # simfolder = grid.save_simulation("mmi")  # initializing environment to save simulation data
    #
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

    grid.run(total_time=time)
    # grid.save_data()

    # df = np.load(os.path.join(simfolder, "detector_readings.npz"))
    # fdtd.dB_map_2D(df["detector (E)"])

    grid.visualize(z=0, show=True)
