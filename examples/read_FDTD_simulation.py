from photfdtd import Grid

if __name__ == "__main__":
    # 读取保存的监视器数据
    filepath = "E:\Github_Clone\photfdtd\examples\\test_star"
    data = Grid.read_simulation(folder=filepath)
    Grid.plot_field(grid=data["grid"], field="E", field_axis="x", axis="x", axis_index=25, folder=filepath)
    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(folder=filepath, data=data, field="E", field_axis="x",
                        index=5, name_det="detector1")



