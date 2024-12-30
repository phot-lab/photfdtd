import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 创建任务和对应的开始和结束日期
tasks = ['Literature review and research design', 'Material experiments and characterization', 'FVM Simulation',
         'Sample preparation and growth', 'Fabrication, tests and data analysis', 'Thesis writing and finalization']
start_dates = ['2025-09-01', '2026-2-01', '2026-12-01', '2027-4-01', '2027-12-01', '2028-08-01']
end_dates = ['2026-2-01', '2026-12-01', '2027-4-01', '2027-12-01', '2028-08-01', '2029-05-01']

# 将字符串日期转换为 datetime 对象
start_dates = [datetime.strptime(date, "%Y-%m-%d") for date in start_dates]
end_dates = [datetime.strptime(date, "%Y-%m-%d") for date in end_dates]

# 创建图形和轴
fig, ax = plt.subplots(figsize=(10, 6))

# 为每个任务绘制横向条形图
for i, task in enumerate(tasks):
    ax.barh(task, (end_dates[i] - start_dates[i]).days, left=start_dates[i], color='orange')

# 设置日期格式
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
# 设置横轴标签显示的间隔
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # 设置每6个月显示一个标签
# 自动旋转日期标签
plt.xticks(rotation=45)

# 设置标题和标签
plt.title("Completion Plan")

# 显示图表
plt.tight_layout()
plt.savefig("甘特图.png")
plt.show()
