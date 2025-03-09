from scipy.signal import windows
import numpy as np
import matplotlib.pyplot as plt

def hanning(frequency, time, cycle):
    duration = cycle / frequency  # 脉冲持续时间
    t = np.linspace(0, duration, int(2 * np.pi / (frequency * 1e-12 / cycle)))  # 计算时间序列
    window = 0.5 * (1 - np.cos(2 * np.pi * t / duration))  # Hanning 窗
    signal = np.sin(2 * np.pi * frequency * t) * window  # 乘以正弦波
    return np.interp(time, t, signal, left=0, right=0)  # 插值以获取当前时刻的值

frequency = 1e9  # 1 GHz
hanning_dt = 1e-12  # 1 ps
cycle = 3  # 3 个周期
t1 = int(2 * np.pi / (frequency * hanning_dt / cycle))

time_steps = np.arange(0, t1) * hanning_dt
hanning_signal = [hanning(frequency, t, cycle) for t in time_steps]

plt.plot(time_steps, hanning_signal)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Hanning Window Modulated Pulse")
plt.show()
