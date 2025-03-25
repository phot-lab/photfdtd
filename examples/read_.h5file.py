import h5py

# 指定 HDF5 文件路径
h5_file_path = "D:\\Github_Clone\\photfdtd\\examples\\basic_ex\\detector1_E.h5"  # 替换为你的文件路径

# 打开 HDF5 文件
with h5py.File(h5_file_path, "r") as f:
    # 打印文件中的所有数据集（类似于查看文件目录）
    def print_h5_structure(name, obj):
        print(name, "->", obj)


    f.visititems(print_h5_structure)  # 遍历并打印 HDF5 文件结构

    # 读取某个数据集（假设文件中有 "E" 数据集）
    if "E" in f:
        data = f["E"][:]  # 读取整个数据集
        print("E shape:", data.shape)  # 打印数据形状
        print("E dtype:", data.dtype)  # 打印数据类型
    else:
        print("Dataset 'E' not found in the file.")
