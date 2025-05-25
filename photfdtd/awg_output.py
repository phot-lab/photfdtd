import numpy as np
from .arc import Arc
from .fiber import Circle
from .waveguide import Waveguide  # 确保导入各种波导类
from .ysplitter import Taper


class AWG_output:
    """
    有Nch个的输出波导的输出耦合端，Ng个阵列波导
    x, y, z: 中心坐标
    lam0: 中心波长
    d: 相邻阵列波导中心间距
    delta_angle_1: 相邻阵列波导的夹角，角度制
    delta_x: 相邻输出波导的中心间距
    w: 波导芯层宽度
    h: 波导芯层厚度
    L_FPR: FPR的长度
    Ng: 阵列波导数
    Nch:AWG的信道数
    W_taper_out: 输出波导与FPR连接处taper的宽度
    L_taper_out: 输出波导与FPR连接处taper的长度
    W_taper_array: 阵列波导与FPR连接处taper的宽度
    L_taper_array: 阵列波导与FPR连接处taper的长度
    refractive_index: 芯层折射率
    L_out: 输入波导长度
    L_array: 阵列波导直波导的长度
    priority: 优先级
    name:名称
    """
    def __init__(self,
                 x: int or float = None,
                 y: int or float = None,
                 z: int or float = None,
                 lam0: int or float = None,
                 d: int or float = None,
                 delta_angle_1: int or float = None,
                 delta_x: int or float = None,
                 w: int or float = None,
                 h: int or float = None,
                 L_FPR: int or float = None,
                 Ng: int or float = None,
                 Nch: int or float = None,
                 W_taper_out: int or float = None,
                 L_taper_out: int or float = None,
                 W_taper_array: int or float = None,
                 L_taper_array: int or float = None,
                 L_out: int or float = None,
                 L_array: int or float = None,
                 refractive_index: float = None,
                 name: str = "awg_out",
                 grid=None,  # 添加grid参数以访问单位处理
                 priority: int = 1) -> None:
        # 自动选择仿真区域中心
        self.x = x if x is not None else int(grid._grid_xlength / 2)
        self.y = y if y is not None else int(grid._grid_ylength / 2)
        self.z = z if z is not None else int(grid._grid_zlength / 2)

        # 保留未转换的参数
        self.lam0=lam0
        self.d=d
        self.delta_angle_1 = delta_angle_1
        self.delta_x=delta_x
        self.w=w
        self.h=h
        self.L_FPR=L_FPR
        self.Ng = Ng
        self.Nch=Nch
        self.L_taper_out = L_taper_out or 0  # 赋默认值为 0
        self.W_taper_out = W_taper_out or 0  # 赋默认值为 0
        self.W_taper_array=W_taper_array or 0
        self.L_taper_array=L_taper_array or 0
        self.L_out=L_out
        self.L_array=L_array
        self.refractive_index=refractive_index
        self.grid=grid
        self.priority=priority
        self.name = name
        self._internal_objects = []# 定义内部对象列表
        #对部分参数进行单位转换，转换后的结果用原名称+0表示
        converted_params = grid._handle_unit(
         [self.x, self.y, self.z, self.lam0,
          self.d, self.delta_x, self.w, self.h, self.L_FPR,
          self.W_taper_out, self.L_taper_out, self.W_taper_array, self.L_taper_array, self.L_out, self.L_array],
          grid_spacing=grid._grid.grid_spacing)
        #解压后的参数
        (self.x0, self.y0, self.z0, self.lam0_0, self.d0,
         self.delta_x0, self.w0, self.h0, self.L_FPR0, self.W_taper_out0,
         self.L_taper_out0, self.W_taper_array0, self.L_taper_array0, self.L_out0, self.L_array0) = converted_params




        self.add_roland_circle_out()  # 添加罗兰圆
        self.add_grating_arc_out()  # 添加光栅圆
        self.add_trapezoid_out()  # 添加连接罗兰圆和光栅圆的倒梯形
        if self.L_taper_out > 0 and self.W_taper_out > 0:  # 检查是否添加 taper
           self.add_taper_out_left()  # 添加连接输出波导和FPR区左侧的taper_in
        if self.L_taper_out > 0 and self.W_taper_out > 0:  # 检查是否添加 taper
           self.add_taper_out_right()  # 添加连接输出波导和FPR区右侧的taper_in
        self.add_waveguide_out_left()#添加左侧输出波导
        self.add_waveguide_out_right()#添加右侧输出波导
        if self.W_taper_array and self.L_taper_array> 0:  # 检查是否添加 taper_array
           self.add_taper_array_out_left()  # 添加连接阵列波导和FPR区左侧的taper_array
           self.add_taper_array_out_right()  # 添加连接阵列波导和FPR区右侧的taper_array
        self.add_waveguide_S1_out_left()  # 添加阵列波导直波导S1部分左侧波导
        self.add_waveguide_S1_out_right()  # 添加阵列波导直波导S1部分右侧波导
        # self.add_arc_and_waveguide_S2_left()  # 添加阵列波导左侧弯曲连接波导和直波导S2#todo:代码未完善
        # self.add_arc_and_waveguide_S2_right()  # 添加阵列波导右侧弯曲连接波导和直波导S2


    # 添加罗兰圆
    def add_roland_circle_out(self):
        angle0=np.radians(-120)
        angle1=np.radians(60)
        roland_circle = Arc(x=self.x,
               y=self.y,
               z=self.z,
               outer_radius=self.L_FPR/2,
               width=self.L_FPR/2,
               ylength=self.h,
               angle_phi=angle0,
               angle_psi=angle1,
               name="roland_circle",
               refractive_index=self.refractive_index,
               grid=self.grid,
               priority=self.priority
        )
        self._internal_objects.append(roland_circle)
    def add_grating_arc_out(self):
          #修改后的代码：
          x2=self.x
          z2=int(self.z-self.L_FPR0 / 2)
          angle=(1.25*self.Ng)*self.d/self.L_FPR
          angle0=np.pi/2-angle/2#用阵列波导数目来控制光栅圆展开角度
          arc_grating = Arc(
               x=x2,
               y=self.y,
               z=z2,
               outer_radius=self.L_FPR ,
               width=self.L_FPR,
               ylength=self.h,
               angle_phi=angle0,
               angle_psi=angle,
               name="arc_grating",
               refractive_index=self.refractive_index,
               grid=self.grid,
               priority=self.priority
           )
          self._internal_objects.append(arc_grating)


    # 添加连接罗兰圆和光栅圆的倒梯形
    def add_trapezoid_out(self):
          #计算梯形的各个参数
          angle=(1.25*self.Ng)*self.d/self.L_FPR#光栅圆展开角度（圆心角）,弧度
          xlength_upper=2*self.L_FPR*np.sin(angle/2)#梯形上底
          xlength_lower=self.L_FPR/2#梯形下底边
          zlength = self.L_FPR * np.cos(angle / 2) + (np.sqrt(3)/2 - 1) * self.L_FPR / 2#梯形的高

          #梯形的中心位置
          x_trapezoid=self.x
          y_trapezoid=self.y
          z_trapezoid=int((self.L_FPR0 * np.cos(angle / 2) -self.L_FPR0 / 2-(np.sqrt(3)/2) * self.L_FPR0 / 2)/2+self.z)

          # 创建倒梯形
          trapezoid = Taper(
               xlength_upper=xlength_upper,
               xlength_lower=xlength_lower,
               ylength=self.h,
               zlength=zlength,
               x=x_trapezoid,
               y=y_trapezoid,
               z=z_trapezoid,
               name="trapezoid",
               refractive_index=self.refractive_index,
               grid=self.grid,
               priority=self.priority)
           # 将倒梯形对象添加到内部对象列表
          self._internal_objects.append(trapezoid)

     # 添加连接输出波导和FPR区左侧的taper_in
    def add_taper_out_left(self):
        self.taper_out_left = []

        if self.Nch % 2 == 0:  # 如果 Nch 为偶数
           self.Nch_taper = self.Nch // 2
           for n in range(1, self.Nch_taper + 1):
               # 计算 taper 的中心坐标
               x_taper_out = int(self.x - (self.L_FPR0 + self.L_taper_out0/2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_taper_out = self.y  # y 轴位置保持不变
               z_taper_out = int(self.z - (self.L_FPR0 + self.L_taper_out0/2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Taper 对象
               taper = Taper(
                    xlength_lower=self.w,
                    xlength_upper=self.W_taper_out,
                    zlength=self.L_taper_out,
                    ylength=self.h,
                    x=x_taper_out,
                    y=y_taper_out,
                    z=z_taper_out,
                    refractive_index=self.refractive_index,
                    name=f"taper_out_left_{n}",
                    grid=self.grid,
                    priority=self.priority
                )

                # 旋转 Taper
               center = [x_taper_out, y_taper_out, z_taper_out]
               taper.rotate_Y(angle=-(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1), center=center, angle_unit=True)

               # 添加到 taper_out_left 列表
               self.taper_out_left.append(taper)
               # 同时添加到内部对象列表
               self._internal_objects.append(taper)

        else:  # 如果 Nch 为奇数
           self.Nch_taper = (self.Nch - 1) // 2
           for n in range(self.Nch_taper + 1):  # 需要加 1 因为中间的 taper 也要包含
               # 计算 taper 的中心坐标
               x_taper_out = int(self.x - (self.L_FPR0 + self.L_taper_out0/2) * np.sin(np.radians(n * self.delta_angle_1)))
               y_taper_out = self.y  # y 轴位置保持不变
               z_taper_out = int(self.z - (self.L_FPR0 + self.L_taper_out0/2) * np.cos(np.radians(n * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Taper 对象
               taper = Taper(
                    xlength_lower=self.w,
                    xlength_upper=self.W_taper_out,
                    zlength=self.L_taper_out,
                    ylength=self.h,
                    x=x_taper_out,
                    y=y_taper_out,
                    z=z_taper_out,
                    refractive_index=self.refractive_index,
                    name=f"taper_out_left_{n + 1}",
                    grid=self.grid,
                    priority=self.priority
                )

               # 旋转 Taper
               center = [x_taper_out, y_taper_out, z_taper_out]
               taper.rotate_Y(angle=-( n  * self.delta_angle_1), center=center, angle_unit=True)

               # 添加到 taper_out_left 列表
               self.taper_out_left.append(taper)
               # 同时添加到内部对象列表
               self._internal_objects.append(taper)




     # 添加连接输出波导和FPR区右侧的taper_in
    def add_taper_out_right(self):
        self.taper_out_right = []

        if self.Nch % 2 == 0:  # 如果 Nch 为偶数
           self.Nch_taper = self.Nch // 2
           for n in range(1, self.Nch_taper + 1):
               # 计算 taper 的中心坐标
               x_taper_out = int(self.x + (self.L_FPR0 + self.L_taper_out0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_taper_out = self.y  # y 轴位置保持不变
               z_taper_out = int(self.z - (self.L_FPR0 + self.L_taper_out0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Taper 对象
               taper = Taper(
                    xlength_lower=self.w,
                    xlength_upper=self.W_taper_out,
                    zlength=self.L_taper_out,
                    ylength=self.h,
                    x=x_taper_out,
                    y=y_taper_out,
                    z=z_taper_out,
                    refractive_index=self.refractive_index,
                    name=f"taper_out_right_{n}",
                    grid=self.grid,
                    priority=self.priority
                )

                # 旋转 Taper
               center = [x_taper_out, y_taper_out, z_taper_out]
               taper.rotate_Y(angle=self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1, center=center, angle_unit=True)

               # 添加到 taper_out_right 列表
               self.taper_out_right.append(taper)
               # 同时添加到内部对象列表
               self._internal_objects.append(taper)

        else:  # 如果 Nch 为奇数
           self.Nch_taper = (self.Nch - 1) // 2
           for n in range(self.Nch_taper + 1):  # 需要加 1 因为中间的 taper 也要包含
                # 计算 taper 的中心坐标
               x_taper_out = int(self.x + (self.L_FPR0 + self.L_taper_out0 / 2) * np.sin(np.radians(n * self.delta_angle_1)))
               y_taper_out = self.y  # y 轴位置保持不变
               z_taper_out = int(self.z - (self.L_FPR0 + self.L_taper_out0 / 2) * np.cos(np.radians(n * self.delta_angle_1)) + self.L_FPR0 / 2)

                # 创建并添加 Taper 对象
               taper = Taper(
                     xlength_lower=self.w,
                     xlength_upper=self.W_taper_out,
                     zlength=self.L_taper_out,
                     ylength=self.h,
                     x=x_taper_out,
                     y=y_taper_out,
                     z=z_taper_out,
                     refractive_index=self.refractive_index,
                     name=f"taper_out_right_{n + 1}",
                     grid=self.grid,
                     priority=self.priority
                 )

                 # 旋转 Taper
               center = [x_taper_out, y_taper_out, z_taper_out]
               taper.rotate_Y(angle=n * self.delta_angle_1, center=center, angle_unit=True)

                # 添加到 taper_out_right 列表
               self.taper_out_right.append(taper)
               # 同时添加到内部对象列表
               self._internal_objects.append(taper)



     # 添加左侧的输出波导
    def add_waveguide_out_left(self):
        self.waveguide_out_left = []
        if self.Nch % 2 == 0:  # 如果 Nch 为偶数
           self.Nch_out = self.Nch // 2
           for n in range(1, self.Nch_out + 1):  # 从 1 到 Nch_out，确保是偶数个波导
               # 计算波导的中心坐标
               x_waveguide_out = int(self.x - (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_waveguide_out = self.y
               z_waveguide_out = int(self.z - (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Waveguide 对象
               waveguide = Waveguide(
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_out,
                   x=x_waveguide_out,
                   y=y_waveguide_out,
                   z=z_waveguide_out,
                   name=f"waveguide_out_left_{n}",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
                )

               # 旋转波导
               center = [x_waveguide_out, y_waveguide_out, z_waveguide_out]
               waveguide.rotate_Y(angle=-(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1), center=center, angle_unit=True)

               # 添加到 waveguide_out_left 列表
               self.waveguide_out_left.append(waveguide)
               self._internal_objects.append(waveguide)

        else:  # 如果 Nch 为奇数
           self.Nch_out = (self.Nch - 1) // 2
           for n in range(self.Nch_out + 1):  # 从 0 到 Nch_out，确保是奇数个波导
               # 计算波导的中心坐标
               x_waveguide_out = int(self.x + (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.sin(np.radians(n * self.delta_angle_1)))
               y_waveguide_out = self.y
               z_waveguide_out = int(self.z - (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.cos(np.radians(n * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Waveguide 对象
               waveguide = Waveguide(
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_out,
                   x=x_waveguide_out,
                   y=y_waveguide_out,
                   z=z_waveguide_out,
                   name=f"waveguide_out_left_{n + 1}",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
                )

               # 旋转波导
               center = [x_waveguide_out, y_waveguide_out, z_waveguide_out]
               waveguide.rotate_Y(angle=-n * self.delta_angle_1, center=center, angle_unit=True)

               # 添加到 waveguide_out_left 列表
               self.waveguide_out_left.append(waveguide)
               self._internal_objects.append(waveguide)


    # 添加右侧的输出波导
    def add_waveguide_out_right(self):
        self.waveguide_out_right = []
        if self.Nch % 2 == 0:  # 如果 Nch 为偶数
           self.Nch_out = self.Nch // 2
           for n in range(1, self.Nch_out + 1):  # 从 1 到 Nch_out，确保是偶数个波导
               # 计算波导的中心坐标
               x_waveguide_out = int(self.x + (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_waveguide_out = self.y
               z_waveguide_out = int(self.z - (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Waveguide 对象
               waveguide = Waveguide(
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_out,
                   x=x_waveguide_out,
                   y=y_waveguide_out,
                   z=z_waveguide_out,
                   name=f"waveguide_out_right_{n}",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
                )

               # 旋转波导
               center = [x_waveguide_out, y_waveguide_out, z_waveguide_out]
               waveguide.rotate_Y(angle=self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1, center=center, angle_unit=True)

               # 添加到 waveguide_out_right 列表
               self.waveguide_out_right.append(waveguide)
               self._internal_objects.append(waveguide)

        else:  # 如果 Nch 为奇数
           self.Nch_out = (self.Nch - 1) // 2
           for n in range(self.Nch_out + 1):  # 从 0 到 Nch_out，确保是奇数个波导
               # 计算波导的中心坐标
               x_waveguide_out = int(self.x + (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.sin(np.radians(n * self.delta_angle_1)))
               y_waveguide_out = self.y
               z_waveguide_out = int(self.z - (self.L_FPR0 + self.L_taper_out0 + self.L_out0 / 2) * np.cos(np.radians(n * self.delta_angle_1)) + self.L_FPR0 / 2)

               # 创建并添加 Waveguide 对象
               waveguide = Waveguide(
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_out,
                   x=x_waveguide_out,
                   y=y_waveguide_out,
                   z=z_waveguide_out,
                   name=f"waveguide_out_right_{n + 1}",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
                )

               # 旋转波导
               center = [x_waveguide_out, y_waveguide_out, z_waveguide_out]
               waveguide.rotate_Y(angle=n * self.delta_angle_1, center=center, angle_unit=True)

               # 添加到 waveguide_out_right 列表
               self.waveguide_out_right.append(waveguide)
               self._internal_objects.append(waveguide)


    # 添加连接阵列波导和FPR区左侧的taper_array
    def add_taper_array_out_left(self):
         self.taper_array_left = []  # 用于存储多个 Taper 实例

         if self.Ng % 2 == 0:  # 如果 Ng 是偶数
            self.N_taper = int(self.Ng / 2)
            for n in range(1, self.N_taper+1):  # n 从 1 到 N_taper
               # 计算每个 taper 的坐标
               x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

               # 创建一个新的 Taper 实例并添加到列表中
               taper = Taper(
                       x=x_n,
                       y=y_n,
                       z=z_n,
                       xlength_upper=self.w,
                       xlength_lower=self.W_taper_array,
                       zlength=self.L_taper_array,
                       ylength=self.h,
                       refractive_index=self.refractive_index,
                       name=f"taper_array_left_{n}",
                       grid=self.grid,
                       priority=self.priority
                )

               # 旋转波导
               center = [x_n, y_n, z_n]
               taper.rotate_Y(angle=self.delta_angle_1/2+(n-1) * self.delta_angle_1, center=center, angle_unit=True)

               # 添加到 taper_array_left 和内部对象列表中
               self.taper_array_left.append(taper)
               self._internal_objects.append(taper)

         else:  # 如果 Ng 是奇数
             self.N_taper = int((self.Ng - 1) / 2)  # 奇数情况下的 taper 数量

             for n in range(self.N_taper + 1):  # n 从 0 到 N_taper
                 # 计算每个 taper 的坐标
                  x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 / 2) * np.sin(n * np.radians(self.delta_angle_1)))
                  y_n = self.y
                  z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * np.cos(n * np.radians(self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

                   # 创建一个新的 Taper 实例并添加到列表中
                  taper = Taper(
                        x=x_n,
                        y=y_n,
                        z=z_n,
                        xlength_upper=self.w,
                        xlength_lower=self.W_taper_array,
                        zlength=self.L_taper_array,
                        ylength=self.h,
                        refractive_index=self.refractive_index,
                        name=f"taper_array_left_{n+1}",
                        grid=self.grid,
                        priority=self.priority
                   )

                  # 旋转波导
                  center = [x_n, y_n, z_n]
                  taper.rotate_Y(angle=n * self.delta_angle_1, center=center, angle_unit=True)

                  # 添加到 taper_array_left 和内部对象列表中
                  self.taper_array_left.append(taper)
                  self._internal_objects.append(taper)


     # 添加连接阵列波导和FPR区右侧的taper_array
    def add_taper_array_out_right(self):
        self.taper_array_right = []

        if self.Ng % 2 == 0:  # 如果 Ng 是偶数
           self.N_taper = int(self.Ng / 2)
           for n in range(1, self.N_taper+1):  # n 从 1 到 N_taper
               # 计算每个 taper 的坐标
               x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

               # 创建一个新的 Taper 实例并添加到列表中
               taper = Taper(
                       x=x_n,
                       y=y_n,
                       z=z_n,
                       xlength_upper=self.w,
                       xlength_lower=self.W_taper_array,
                       zlength=self.L_taper_array,
                       ylength=self.h,
                       refractive_index=self.refractive_index,
                       name=f"taper_array_right_{n}",
                       grid=self.grid,
                       priority=self.priority
                )

               # 旋转波导
               center = [x_n, y_n, z_n]
               taper.rotate_Y(angle=-(self.delta_angle_1/2+(n-1) * self.delta_angle_1), center=center, angle_unit=True)

               # 添加到 taper_array_left 和内部对象列表中
               self.taper_array_left.append(taper)
               self._internal_objects.append(taper)

        else:  # 如果 Ng 是奇数
             self.N_taper = int((self.Ng - 1) / 2)  # 奇数情况下的 taper 数量

             for n in range(self.N_taper + 1):  # n 从 0 到 N_taper
                 # 计算每个 taper 的坐标
                  x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 / 2) * np.sin(n * np.radians(self.delta_angle_1)))
                  y_n = self.y
                  z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * np.cos(n * np.radians(self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

                   # 创建一个新的 Taper 实例并添加到列表中
                  taper = Taper(
                        x=x_n,
                        y=y_n,
                        z=z_n,
                        xlength_upper=self.w,
                        xlength_lower=self.W_taper_array,
                        zlength=self.L_taper_array,
                        ylength=self.h,
                        refractive_index=self.refractive_index,
                        name=f"taper_array_right_{n}",
                        grid=self.grid,
                        priority=self.priority
                   )

                  # 旋转波导
                  center = [x_n, y_n, z_n]
                  taper.rotate_Y(angle=-n * self.delta_angle_1, center=center, angle_unit=True)


                  # 添加到 taper_array_left 和内部对象列表中
                  self.taper_array_left.append(taper)
                  self._internal_objects.append(taper)


     #添加阵列波导直波导S1部分左侧波导
    def add_waveguide_S1_out_left(self):
        self.waveguide_S1_left = []
        if self.Ng % 2 == 0:  # 如果 Ng 是偶数
           self.N_taper = int(self.Ng / 2)
           for n in range(1, self.N_taper + 1):  # n 从 1 到 N_taper
               # 计算每个波导的坐标
               x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)

               # 创建 Waveguide 实例
               waveguide = Waveguide(
                    x=x_n,
                    y=y_n,
                    z=z_n,
                    xlength=self.w,
                    ylength=self.h,
                    zlength=self.L_array,
                    refractive_index=self.refractive_index,
                    name=f"waveguide_S1_left_{n}",
                    grid=self.grid,
                    priority=self.priority
                )

               # 旋转波导
               center = [x_n, y_n, z_n]
               waveguide.rotate_Y(angle=self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1, center=center, angle_unit=True)

               # 添加到 waveguide_S1_left 列表
               self.waveguide_S1_left.append(waveguide)

               # 同时添加到内部对象列表
               self._internal_objects.append(waveguide)

        else:  # 如果 Ng 是奇数
             self.N_taper = int((self.Ng - 1) / 2)  # 奇数情况下的 taper 数量
             for n in range(self.N_taper + 1):  # 因为中间也是算一个，所以要加1
                 # 计算每个波导的坐标
                 x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.sin(n * np.radians(self.delta_angle_1)))
                 y_n = self.y
                 z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.cos(n * np.radians(self.delta_angle_1)) - self.L_FPR0 / 2)

                # 创建 Waveguide 实例
                 waveguide = Waveguide(
                        x=x_n,
                        y=y_n,
                        z=z_n,
                        xlength=self.w,
                        ylength=self.h,
                        zlength=self.L_array,
                        refractive_index=self.refractive_index,
                        name=f"waveguide_S1_left_{n+1}",
                        grid=self.grid,
                        priority=self.priority
                  )

                 # 旋转波导
                 center = [x_n, y_n, z_n]
                 waveguide.rotate_Y(angle=n * self.delta_angle_1, center=center, angle_unit=True)

                # 添加到 waveguide_S1_left 列表
                 self.waveguide_S1_left.append(waveguide)

               # 同时添加到内部对象列表
                 self._internal_objects.append(waveguide)

    #添加阵列波导直波导S1部分右侧波导
    def add_waveguide_S1_out_right(self):
          self.waveguide_S1_right= []
          if self.Ng % 2 == 0:  # 如果 Ng 是偶数
             self.N_taper = int(self.Ng / 2)
             for n in range(1, self.N_taper + 1):  # n 从 1 到 N_taper
                 # 计算每个波导的坐标
                 x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.sin(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
                 y_n = self.y
                 z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.cos(np.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)

                 # 创建 Waveguide 实例
                 waveguide = Waveguide(
                   x=x_n,
                   y=y_n,
                   z=z_n,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_array,
                   refractive_index=self.refractive_index,
                   name=f"waveguide_S1_right_{n}",
                   grid=self.grid,
                   priority=self.priority
                  )

                 # 旋转波导
                 center = [x_n, y_n, z_n]
                 waveguide.rotate_Y(angle=-self.delta_angle_1 / 2 - (n - 1) * self.delta_angle_1, center=center, angle_unit=True)

                 # 添加到 waveguide_S1_right 列表
                 self.waveguide_S1_right.append(waveguide)

                 # 同时添加到内部对象列表
                 self._internal_objects.append(waveguide)

          else:  # 如果 Ng 是奇数
             self.N_taper = int((self.Ng - 1) / 2)  # 奇数情况下的 taper 数量
             for n in range(self.N_taper + 1):  # 因为中间也是算一个，所以要加1
                 # 计算每个波导的坐标
                x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.sin(n * np.radians(self.delta_angle_1)))
                y_n = self.y
                z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * np.cos(n * np.radians(self.delta_angle_1)) - self.L_FPR0 / 2)

                # 创建 Waveguide 实例
                waveguide = Waveguide(
                    x=x_n,
                    y=y_n,
                    z=z_n,
                    xlength=self.w,
                    ylength=self.h,
                    zlength=self.L_array,
                    refractive_index=self.refractive_index,
                    name=f"waveguide_S1_right_{n+1}",
                    grid=self.grid,
                    priority=self.priority
                 )

                 # 旋转波导
                center = [x_n, y_n, z_n]
                waveguide.rotate_Y(angle=-n * self.delta_angle_1, center=center, angle_unit=True)

                # 添加到 waveguide_S1_right 列表
                self.waveguide_S1_right.append(waveguide)

                # 同时添加到内部对象列表
                self._internal_objects.append(waveguide)


    #todo:没有区分奇数和偶数的阵列波导（下面只考虑了奇数的情况）
    ## 添加阵列波导左侧弯曲连接波导和直波导S2
    #中间直波导S2写在这个模块
    def add_arc_and_waveguide_S2_left(self):
        self.arc_left = []
        self.waveguide_S2_left = []
        H0 = (self.L_array0 + self.L_taper_array0+self.L_FPR0) * np.tan(np.radians(self.delta_angle_1))#计算坐标
        H = (self.L_array+self.L_taper_array+ self.L_FPR) * np.tan(np.radians(self.delta_angle_1))#计算长度
        xC_0=self.x#中间直波导S2的坐标
        zC_0=int(self.z+(self.L_array0 +self.L_taper_array0+ self.L_FPR0)- self.L_FPR0 / 2)
        #中间直波导S2
        waveguide_S2_left0 = Waveguide(
                   x=xC_0,
                   y=self.y,
                   z=zC_0,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_array*2,
                   name="waveguide_S2_left0",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(waveguide_S2_left0)
        #阵列波导左侧弯曲连接波导和直波导S2
        xA_1=self.x#左侧第一个歪曲波导的圆心坐标
        zA_1=int(self.z+(self.L_array0 +self.L_taper_array0+ self.L_FPR0) * np.cos( np.radians(self.delta_angle_1)) - self.L_FPR0 / 2+ H0 * np.sin(np.radians(self.delta_angle_1)))
        xC_1=int(xA_1-H0)#左侧第一个直波导S2的坐标
        zC_1=int(zA_1 + self.L_array0 / 2)

        waveguide_S2_left1 = Waveguide(
                   x=xC_1,
                   y=self.y,
                   z=zC_1,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_array,
                   name="waveguide_S2_left1",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(waveguide_S2_left1)
        arc_left1 = Arc(
                    outer_radius=H + self.w / 2,
                    width=self.w,
                    x=xA_1,
                    y=self.y,
                    z=zA_1,
                    ylength=self.h,
                    angle_phi=np.pi,
                    angle_psi=np.radians(self.delta_angle_1),
                    name="arc_left1",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(arc_left1)


        for n in range(2,self.N_taper+1):
            xB = int(self.x-(self.L_array0 +self.L_taper_array0+ self.L_FPR0) * np.sin((n-1) * np.radians(self.delta_angle_1)))
            zB = int(self.z+(self.L_array0 +self.L_taper_array0+ self.L_FPR0) * np.cos((n-1) * np.radians(self.delta_angle_1)) - self.L_FPR0 / 2)
            xA = xB#弯曲波导的圆心坐标
            zA = zB
            xC = int(xA -H0)#直波导S2的中心坐标
            zC = int(zA + self.L_array0 / 2)

            waveguide = Waveguide(
                   x=xC,
                   y=self.y,
                   z=zC,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_array,
                   name=f"waveguide_S2_left{n}",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
             )
            self.waveguide_S2_left.append(waveguide)
            # 同时添加到内部对象列表
            self._internal_objects.append(waveguide)

            arc = Arc(
                    outer_radius=H + self.w / 2,
                    width=self.w,
                    x=xA,
                    y=self.y,
                    z=zA,
                    ylength=self.h,
                    angle_phi=np.pi,
                    angle_psi=np.radians(n*self.delta_angle_1),
                    name=f"arc_left{n}",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
            self.arc_left.append(arc)
            # 同时添加到内部对象列表
            self._internal_objects.append(arc)


    #添加阵列波导右侧弯曲连接波导和直波导S2
    def add_arc_and_waveguide_S2_right(self):
        self.arc_right = []
        self.waveguide_S2_right = []
        H0 = (self.L_array0 + self.L_taper_array0+self.L_FPR0) * np.tan(np.radians(self.delta_angle_1))#计算坐标
        H = (self.L_array+self.L_taper_array+ self.L_FPR) * np.tan(np.radians(self.delta_angle_1))#计算长度
        xA_1=self.x
        zA_1=int(self.z+(self.L_array0 +self.L_taper_array0+ self.L_FPR0) * np.cos( np.radians(self.delta_angle_1)) - self.L_FPR0 / 2+ H0 * np.sin(np.radians(self.delta_angle_1)))
        xC_1=int(xA_1+H0)
        zC_1=int(zA_1 + self.L_array0 / 2)
        waveguide_S2_right1 = Waveguide(
                   x=xC_1,
                   y=self.y,
                   z=zC_1,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_array,
                   name="waveguide_S2_right1",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(waveguide_S2_right1)
        arc_right1 = Arc(
                    outer_radius=H + self.w / 2,
                    width=self.w,
                    x=xA_1,
                    y=self.y,
                    z=zA_1,
                    ylength=self.h,
                    angle_phi=-np.radians(self.delta_angle_1),
                    angle_psi=np.radians(self.delta_angle_1),
                    name="arc_right1",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(arc_right1)


        for n in range(2,self.N_taper+1):
            xB = int(self.x+(self.L_array0 +self.L_taper_array0+ self.L_FPR0) * np.sin((n-1) * np.radians(self.delta_angle_1)))
            zB = int(self.z+(self.L_array0 +self.L_taper_array0+ self.L_FPR0) * np.cos((n-1) * np.radians(self.delta_angle_1)) - self.L_FPR0 / 2)
            xA = xB
            zA = zB
            xC = int(xA+H0)
            zC = int(zA + self.L_array0 / 2)


            waveguide = Waveguide(
                   x=xC,
                   y=self.y,
                   z=zC,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=self.L_array,
                   name=f"waveguide_S2_right{n}",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
             )
            self.waveguide_S2_right.append(waveguide)
            # 同时添加到内部对象列表
            self._internal_objects.append(waveguide)

            arc = Arc(
                    outer_radius=H + self.w / 2,
                    width=self.w,
                    x=xA,
                    y=self.y,
                    z=zA,
                    ylength=self.h,
                    angle_phi=-np.radians(n*self.delta_angle_1),
                    angle_psi=np.radians(n*self.delta_angle_1),
                    name=f"arc_right{n}",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
            self.arc_right.append(arc)
            # 同时添加到内部对象列表
            self._internal_objects.append(arc)



