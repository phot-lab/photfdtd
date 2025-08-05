from photfdtd import Grid
"""This example demonstrates all the visualization functions. Plz refer to photfdtd.fdtd.visualization.py for more details.
本示例演示了所有可视化函数。请参阅 photfdtd.fdtd.visualization.py 以获取更多详细信息。"""

if __name__ == "__main__":
    # 读取保存的grid
    filepath = ".\\basic_ex"
    grid = Grid.read_simulation(folder=filepath)
    
    """General visualization function, all specific visualization functions will be run by simply running this function.
    通用可视化函数，所有特定可视化函数都可以通过此函数调用。一般情况下仅用这个即可。"""
    grid.visualize()

    """Specific visualization functions"""
    # Demonstration of the grid. Set show_energy=True to visualize the energy distribution.
    # 绘制grid的结构。设置show_energy=True以可视化能量分布。
    grid.save_fig(show_energy=True)

    # Plot the refractive index distribution in the grid. Set axis and axis_index to specify the axis.
    # 绘制网格中的折射率分布。设置axis和axis_index以指定轴。
    grid.plot_n(axis="z",axis_index=0)

    # Plot the dB_map of a blockdetector, unavailable yet.
    # 绘制blockdetector的dB_map，目前不可用。
    # Grid.dB_map(grid=grid)

    # Plot the field distribution of the final cut of simulation.
    # 绘制仿真结束时刻的场分布。
    grid.plot_field(axis="y", axis_index=0, field="E", field_axis="x", folder=None, cmap="jet",
                   show_geometry=True, show_field=True, vmax=None, vmin=None)

    # Plot the result of a detector, returns a tuple of frequencies and the spectrum.
    # 绘制探测器的结果，返回频率和光谱。
    freqs, spectrum1 = grid.visualize_single_detector(name_det="detector1")

    # Plot the results of all detectors in the grid. This method simply run visualize_single_detector for each detector.
    # 绘制网格中所有探测器的结果。此方法对每个探测器运行 visualize_single_detector。
    grid.visualize_detectors()
