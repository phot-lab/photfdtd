from dataclasses import dataclass


@dataclass
class Subregion:
    direction: str
    cell_size: float
    region_start: float
    region_end: float
    transition_length: float


# 单元格尺寸
dx = 0.002
dy = 0.002
dz = 0.000095

# 定义子区域
subregions = [
    Subregion(direction='x', cell_size=1e-3, region_start=27e-3, region_end=33e-3, transition_length=5e-3),
    Subregion(direction='y', cell_size=1e-3, region_start=7e-3, region_end=13e-3, transition_length=5e-3),
    Subregion(direction='x', cell_size=1e-3, region_start=-2e-3, region_end=4e-3, transition_length=5e-3),
    Subregion(direction='x', cell_size=1e-3, region_start=56e-3, region_end=62e-3, transition_length=5e-3),
    Subregion(direction='y', cell_size=1e-3, region_start=28e-3, region_end=32e-3, transition_length=5e-3),
]

# 打印所有子区域信息
for i, sub in enumerate(subregions, start=1):
    print(f"Subregion {i}: {sub}")

import numpy as np


class FDTD_Domain:
    def __init__(self, size_x, size_y, size_z, min_x, min_y, min_z):
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z


# 定义 FDTD 域
fdtd_domain = FDTD_Domain(size_x=0.1, size_y=0.1, size_z=0.01, min_x=0, min_y=0, min_z=0)

# 计算网格点数
dx, dy, dz = 0.002, 0.002, 0.000095
nx = round(fdtd_domain.size_x / dx)
ny = round(fdtd_domain.size_y / dy)
nz = round(fdtd_domain.size_z / dz)

# 计算网格节点坐标,E,H分别计算
node_coordinates_xe = np.arange(nx + 1) * dx + fdtd_domain.min_x
node_coordinates_ye = np.arange(ny + 1) * dy + fdtd_domain.min_y
node_coordinates_ze = np.arange(nz + 1) * dz + fdtd_domain.min_z

node_coordinates_xh = np.arange(nx + 2) * dx + fdtd_domain.min_x - dx / 2
node_coordinates_yh = np.arange(ny + 2) * dy + fdtd_domain.min_y - dy / 2
node_coordinates_zh = np.arange(nz + 2) * dz + fdtd_domain.min_z - dz / 2

# 假设 subregions 已经定义
number_of_subregions = len(subregions) if 'subregions' in locals() else 0

# 打印最终网格
print("Final node coordinates (x, y, z):")
print(node_coordinates_xe)
print(node_coordinates_ye)
print(node_coordinates_ze)

# 假设 boundary 是一个包含 is_nonuniform_cpml 属性的对象或字典
boundary = {'is_nonuniform_cpml': True}  # 示例

# 如果需要设置非均匀 CPML
if 'is_nonuniform_cpml' in boundary and boundary['is_nonuniform_cpml']:
    def set_nonuniform_cpml_grid():
        """ 设定非均匀 CPML 网格 (函数实现需要填充) """
        pass  # 这里可以放置具体的 CPML 设定代码


    set_nonuniform_cpml_grid()

# 重新计算网格数量
nx = len(node_coordinates_xe) - 1
ny = len(node_coordinates_ye) - 1
nz = len(node_coordinates_ze) - 1

# 计算网格单元尺寸
cell_sizes_xe = np.diff(node_coordinates_xe)
cell_sizes_ye = np.diff(node_coordinates_ye)
cell_sizes_ze = np.diff(node_coordinates_ze)

# 计算磁场网格的网格单元尺寸
cell_sizes_xh = np.diff(node_coordinates_xh)
cell_sizes_yh = np.diff(node_coordinates_yh)
cell_sizes_zh = np.diff(node_coordinates_zh)

# 更新 FDTD 域的网格坐标
fdtd_domain.node_coordinates_xe = node_coordinates_xe
fdtd_domain.node_coordinates_ye = node_coordinates_ye
fdtd_domain.node_coordinates_ze = node_coordinates_ze

fdtd_domain.node_coordinates_xh = node_coordinates_xh
fdtd_domain.node_coordinates_yh = node_coordinates_yh
fdtd_domain.node_coordinates_zh = node_coordinates_zh

# 计算常用辅助参数
nxp1, nyp1, nzp1 = nx + 1, ny + 1, nz + 1
nxm1, nxm2 = nx - 1, nx - 2
nym1, nym2 = ny - 1, ny - 2
nzm1, nzm2 = nz - 1, nz - 2

# 输出计算结果
print(f"nx: {nx}, ny: {ny}, nz: {nz}")
print(f"nx+1: {nxp1}, ny+1: {nyp1}, nz+1: {nzp1}")
print(f"nx-1: {nxm1}, nx-2: {nxm2}")
print(f"ny-1: {nym1}, ny-2: {nym2}")
print(f"nz-1: {nzm1}, nz-2: {nzm2}")


def insert_subregion_into_domain(node_coordinates_e, node_coordinates_h, subregion, base_cell_size):
    """ 插入子区域到网格，并调整网格坐标 """

    # 计算子区域长度
    subregion_length = subregion["region_end"] - subregion["region_start"]
    n_subregion_cells = round(subregion_length / subregion["cell_size"])
    subregion["cell_size"] = subregion_length / n_subregion_cells

    bcs = base_cell_size
    srcs = subregion["cell_size"]

    # 计算过渡起始位置
    tr_start_position = subregion["region_start"] - subregion["transition_length"]
    tr_start_node = np.argmin(np.abs(node_coordinates_e - tr_start_position))
    tr_length = subregion["region_start"] - node_coordinates_e[tr_start_node]

    # 计算过渡单元数量
    R = (tr_length + bcs) / (tr_length + srcs)
    number_of_transition_cells = int(np.floor(np.log10(bcs / srcs) / np.log10(R)) - 1)

    # 计算过渡单元尺寸
    transition_cell_sizes = srcs * R ** np.arange(1, number_of_transition_cells + 1)

    # 调整总长度
    transition_cell_sizes *= tr_length / np.sum(transition_cell_sizes)

    # 过渡区域单元尺寸
    bsr_transition_cell_sizes = transition_cell_sizes[::-1]
    bsr_tr_start_node = tr_start_node

    # 计算过渡结束位置
    tr_end_position = subregion["region_end"] + subregion["transition_length"]
    tr_end_node = np.argmin(np.abs(node_coordinates_e - tr_end_position))
    tr_length = node_coordinates_e[tr_end_node] - subregion["region_end"]

    # 计算过渡单元尺寸
    asr_transition_cell_sizes = transition_cell_sizes
    asr_tr_end_node = tr_end_node

    # 生成子区域网格单元尺寸
    subregion_cell_sizes_e = np.full(n_subregion_cells, srcs)

    # 合并所有单元尺寸
    sr_all_cs_e = np.concatenate((bsr_transition_cell_sizes, subregion_cell_sizes_e, asr_transition_cell_sizes))

    # 调整网格坐标
    nodes_before_subregion_e = node_coordinates_e[:bsr_tr_start_node]
    nodes_after_subregion_e = node_coordinates_e[asr_tr_end_node:]
    a_node = node_coordinates_e[bsr_tr_start_node]

    n_subregion_cells = len(sr_all_cs_e)
    subregion_node_coordinates_e = np.zeros(n_subregion_cells - 1)

    for si in range(n_subregion_cells - 1):
        a_node += sr_all_cs_e[si]
        subregion_node_coordinates_e[si] = a_node

    node_coordinates_e = np.concatenate(
        (nodes_before_subregion_e, subregion_node_coordinates_e, nodes_after_subregion_e))
    n_nodes = len(node_coordinates_e)

    # 计算磁场网格点坐标（位于单元中心）
    node_coordinates_h = 0.5 * (node_coordinates_e[:-1] + node_coordinates_e[1:])
    node_coordinates_h = np.concatenate(
        ([node_coordinates_e[0] - bcs / 2], node_coordinates_h, [node_coordinates_e[-1] + bcs / 2]))

    return node_coordinates_e, node_coordinates_h


for subregion in subregions:
    if subregion.direction == 'x':
        node_coordinates_xe, node_coordinates_xh = insert_subregion_into_domain(
            node_coordinates_xe, node_coordinates_xh, subregion, dx
        )
    elif subregion.direction == 'y':
        node_coordinates_ye, node_coordinates_yh = insert_subregion_into_domain(
            node_coordinates_ye, node_coordinates_yh, subregion, dy
        )
    elif subregion.direction == 'z':
        node_coordinates_ze, node_coordinates_zh = insert_subregion_into_domain(
            node_coordinates_ze, node_coordinates_zh, subregion, dz
        )

# Example usage:
nodes_e = np.linspace(0, 10, 100)
nodes_h = np.linspace(0.05, 10.05, 100)
subregion = {"region_start": 3, "region_end": 7, "transition_length": 1, "cell_size": 0.1}
base_cell_size = 0.2

result = insert_subregion_into_domain(nodes_e, nodes_h, subregion, base_cell_size)
print(result)
