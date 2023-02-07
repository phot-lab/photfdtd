# 说明

这几个 Python 文件包含了基础器件和光器件的实现和测试用例，使用了fdtd库已经实现了的 Finite-difference time-domain method （时域有限差分）算法。

## 基础器件

1. waveguide - 直波导
2. arc - 圆弧
3. sbend - s波导
4. ysplitter - y分支

## 光器件

光器件由基础器件组成，光器件与光器件之间也可以连接。

1. directional coupler - 方向耦合器
2. mmi - 多模耦合干涉仪
3. ring - 微环