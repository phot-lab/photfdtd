import sys
from pathlib import Path

path = Path()
parent_directory = path.parent.absolute() # 获取父目录

sys.path.append("/Users/lichunyu/VSCode/PassiveOpticalDevices") # 将父目录加入 Python 路径
