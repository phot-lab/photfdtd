from photfdtd import Waveguide, Grid, Solve, Index
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # This example shows a 2D simulation of a basic straight waveguide 本示例展示了一个基础矩形波导的二维仿真
    # set background index设置背景折射率
    background_index = 1.4447

    index_Si = Index(material="Si")
    index_Re_Si, index_Im_Si = index_Si.get_refractive_index(wavelength=1.55e-6)

    # # create the simulation region, which is a Grid object 新建一个 grid 对象
    grid = Grid(grid_xlength=3.5e-6, grid_ylength=1, grid_zlength=5.5e-6,
                grid_spacing_x=20e-9,
                grid_spacing_z=20e-9,
                grid_spacing_y=20e-9,
                permittivity=background_index ** 2,
                foldername="transmission_ex")

    # We can plot the geometry and the index map now
    grid.save_fig()
    # plot the refractive index map on z=0绘制z=0截面折射率分布
    grid.plot_n()

    grid = grid.read_simulation(folder=grid.folder)

    for detector in grid._grid.detectors:
        if detector.name == "detector1":
            signal = detector.flux[:, 0, 2]
    # 参数定义
    fs = 1e15  # 采样频率 (Hz)
    T = len(signal) / fs  # 信号总时间 (s)
    t = np.linspace(0, T, len(signal))  # 时间轴
    freq_range = (1.75e14, 2.15e14)  # 目标频率范围 (Hz)

    # 计算傅里叶变换
    fft_result = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), d=1 / fs)  # 计算频率轴
    magnitude = np.abs(fft_result)

    # 零填充信号
    N = len(t) * 2  # 目标点数为原来的一倍
    signal_padded = np.pad(signal, (0, N - len(signal)), 'constant')

    # 计算傅里叶变换 (零填充后)
    fft_result_padded = np.fft.fft(signal_padded)
    frequencies_padded = np.fft.fftfreq(N, d=1 / fs)
    magnitude_padded = np.abs(fft_result_padded)

    # 绘制时域和频域图
    plt.figure(figsize=(12, 6))

    # 时域信号
    plt.subplot(2, 1, 1)
    plt.plot(t, signal, label="Original Signal")
    plt.plot(np.linspace(0, T, N), signal_padded, label="Zero Padded Signal", linestyle='--')
    plt.title("Time Domain Signal")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.legend()

    # 频域信号
    plt.subplot(2, 1, 2)
    plt.plot(frequencies[:len(frequencies) // 2], magnitude[:len(frequencies) // 2], label="Original FFT")
    plt.plot(frequencies_padded[:len(frequencies_padded) // 2], magnitude_padded[:len(frequencies_padded) // 2],
             label="Zero Padded FFT", linestyle='--')
    plt.title("Frequency Domain (Magnitude Spectrum)")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Magnitude")
    plt.legend()
    plt.grid()

    import os

    plt.tight_layout()
    plt.savefig(os.path.join(grid.folder, f"new_spectrum.png"))
    plt.close()

    grid.visualize()

    grid.calculate_Transmission(detector_name_1="detector1", detector_name_2="detector2", wl_start=1400e-9, wl_end=1700e-9)
