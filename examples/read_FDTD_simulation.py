from photfdtd import Grid

if __name__ == "__main__":
    # 读取保存的监视器数据
    filepath = ".\\basic_ex"
    grid = Grid.read_simulation(folder=filepath)
    Grid.plot_field(grid=grid, field="E", field_axis="x", axis="x", axis_index=25, folder=filepath)
    # 由监视器数据绘制Ex场随时间变化的图像
    Grid.plot_fieldtime(grid=grid, field_axis="x", field="E", index=5, name_det="detector1")



