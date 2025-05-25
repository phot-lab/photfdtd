import numpy as np
import matplotlib.pyplot as plt

# 参数设定
R = 10  # 罗兰圆半径
r = R / 2  # 罗兰圆的半径
xi_value = 0.5  # 假设的输入坐标 xi
a_value = xi_value / r  # 角度 a
xp_value = r * np.tan(a_value)  # 光源坐标 xp

# 绘制图形
fig, ax = plt.subplots(figsize=(8, 8))

# 绘制罗兰圆
circle = plt.Circle((0, 0), r, color='lightgray', fill=True, linestyle='--', label="Roland Circle (r=R/2)")
ax.add_artist(circle)

# 绘制坐标轴
ax.axhline(0, color='black', linewidth=1)
ax.axvline(0, color='black', linewidth=1)

# 绘制光源位置 xp，标出 xi 和角度 a
ax.plot([0, r * np.cos(a_value)], [0, r * np.sin(a_value)], 'g--', label=f'Angle a={a_value:.2f}')  # 角度线
ax.plot(r * np.cos(a_value), r * np.sin(a_value), 'bo', label="光源位置 (xp)")

# 绘制 xi 的位置 (这只是一个参考线，用来说明输入坐标与实际光源的关系)
ax.plot([0, xi_value * r], [0, 0], 'r--', label=f'输入坐标 xi={xi_value}')  # 输入坐标位置

# 绘制 r，表示罗兰圆的半径
ax.plot([0, r], [0, 0], 'k-', label=f'罗兰圆半径 r={r}')  # 半径

# 标注注释
ax.text(r / 2, 0.2, f'R/2 = {r:.2f}', fontsize=12, color='black')
ax.text(xi_value * r, -0.5, f'xi = {xi_value}', fontsize=12, color='red')
ax.text(r * np.cos(a_value), r * np.sin(a_value) + 0.5, f'xp = {xp_value:.2f}', fontsize=12, color='blue')

# 设置图形的标题和标签
ax.set_title('几何关系：xi, a, xp 与罗兰圆的关系')
ax.set_xlabel('横坐标')
ax.set_ylabel('纵坐标')

# 设置比例为相等
ax.set_aspect('equal')

# 设置 x 和 y 轴的范围
ax.set_xlim(-r-1, r+1)
ax.set_ylim(-r-1, r+1)

# 显示图例
ax.legend()

# 显示图形
plt.grid(True)
plt.show()
