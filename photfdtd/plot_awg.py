from photfdtd import AWG_input, AWG_output, Grid, Solve
import numpy as np
class Plot_AWG:
    def __init__(self, lam0, d,  delta_x, w, h, L_FPR, Ng,Nch, L_array,
                 W_taper_out=None, L_taper_out=None, W_taper_in=None, L_taper_in=None,
                 W_taper_array=None, L_taper_array=None, refractive_index=None,
                 background_index=None, grid_xlength=None, grid_ylength=None, grid_zlength=None,
                 grid_spacing=None, foldername=None, priority=None, axis=None, axis_number=None):
        """
        初始化绘图类，配置AWG输入和输出波导的结构参数。

        Parameters:
        lam0: 中心波长
        d: 相邻阵列波导中心间距
        delta_angle_1: 相邻阵列波导的夹角，角度制
        delta_x: 相邻输入波导的中心间距
        w: 波导芯层宽度
        h: 波导芯层厚度
        L_FPR: FPR的长度
        Ng: 阵列波导数
        L_array: 阵列波导长度
        W_taper_out, L_taper_out: 输出波导taper的宽度和长度
        W_taper_in, L_taper_in: 输入波导taper的宽度和长度
        W_taper_array, L_taper_array: 阵列波导与FPR连接处taper的宽度和长度
        refractive_index: 芯层折射率
        background_index: 背景折射率
        grid_xlength, grid_ylength, grid_zlength: 网格尺寸
        grid_spacing: 网格间距
        foldername: 文件夹名
        priority: 优先级
        axis: 绘图的轴
        axis_number: 绘图轴的编号
        """
        # 设置参数
        self.lam0 = lam0
        self.d = d
        self.L_FPR = L_FPR
        self.delta_angle_1 =self.d*180/(self.L_FPR*np.pi)
        self.delta_x = delta_x
        self.w = w
        self.h = h
        self.Ng = Ng
        self.Nch=Nch
        self.L_array = L_array
        self.W_taper_out = W_taper_out
        self.L_taper_out = L_taper_out
        self.W_taper_in = W_taper_in
        self.L_taper_in = L_taper_in
        self.W_taper_array = W_taper_array
        self.L_taper_array = L_taper_array
        self.refractive_index = refractive_index
        self.background_index = background_index
        self.grid_xlength = grid_xlength
        self.grid_ylength = grid_ylength
        self.grid_zlength = grid_zlength
        self.grid_spacing = grid_spacing
        self.foldername = foldername
        self.priority = priority
        self.axis = axis
        self.axis_number = axis_number

    def plot_awg_out(self):
        """
        绘制AWG输出波导的场图和折射率分布。
        """
        # 创建模拟区域，grid对象
        grid = Grid(grid_xlength=self.grid_xlength, grid_ylength=self.grid_ylength, grid_zlength=self.grid_zlength,
                    grid_spacing=self.grid_spacing, permittivity=self.background_index ** 2, foldername=self.foldername)

        # 设置器件参数并创建AWG输出波导对象
        awg_out = AWG_output(
            lam0=self.lam0, d=self.d, delta_angle_1=self.delta_angle_1, delta_x=self.delta_x, w=self.w, h=self.h,
            L_FPR=self.L_FPR, Ng=self.Ng,Nch=self.Nch, L_array=self.L_array, L_out=self.L_array,
            W_taper_out=self.W_taper_out, L_taper_out=self.L_taper_out,
            W_taper_array=self.W_taper_array, L_taper_array=self.L_taper_array,
            refractive_index=self.refractive_index, name="awg_out", grid=grid, priority=self.priority
        )

        # 向grid中添加器件
        grid.add_object(awg_out)

        # 创建Solve对象并绘制截面折射率分布
        solve = Solve(grid=grid, axis=self.axis, index=self.axis_number, filepath=grid.folder)
        solve.plot(image_name="awg_out结构图")

    def plot_awg_in(self):
        """
        绘制AWG输入波导的场图和折射率分布。
        """
        # 创建模拟区域，grid对象
        grid = Grid(grid_xlength=self.grid_xlength, grid_ylength=self.grid_ylength, grid_zlength=self.grid_zlength,
                    grid_spacing=self.grid_spacing, permittivity=self.background_index ** 2, foldername=self.foldername)

        # 设置器件参数并创建AWG输入波导对象
        awg_in = AWG_input(
            lam0=self.lam0, d=self.d, delta_angle_1=self.delta_angle_1, delta_x=self.delta_x, w=self.w, h=self.h,
            L_FPR=self.L_FPR, Ng=self.Ng, L_array=self.L_array, L_in=self.L_array,
            W_taper_in=self.W_taper_in, L_taper_in=self.L_taper_in,
            W_taper_array=self.W_taper_array, L_taper_array=self.L_taper_array,
            refractive_index=self.refractive_index, name="awg_in", grid=grid, priority=self.priority
        )

        # 向grid中添加器件
        grid.add_object(awg_in)

        # 创建Solve对象并绘制截面折射率分布
        solve = Solve(grid=grid, axis=self.axis, index=self.axis_number, filepath=grid.folder)
        solve.plot(image_name="awg_in结构图")

