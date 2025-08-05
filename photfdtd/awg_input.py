import photfdtd.fdtd.backend as bd
from .arc import Arc
from .fiber import Circle
from .waveguide import Waveguide  # 确保导入各种波导类
from .ysplitter import Taper


class AWG_input:
    """
    只有一个输入波导的输入耦合端，Ng个阵列波导
    x, y, z: 中心坐标
    lam0: 中心波长
    d: 相邻阵列波导中心间距
    delta_angle_1: 相邻阵列波导的夹角，角度制
    delta_x: 相邻输入波导的中心间距
    w: 波导芯层宽度
    h: 波导芯层厚度
    L_FPR: FPR的长度
    Ng: 阵列波导数
    W_taper_in: 输入波导与FPR连接处taper的宽度
    L_taper_in: 输入波导与FPR连接处taper的长度
    W_taper_array: 阵列波导与FPR连接处taper的宽度
    L_taper_array: 阵列波导与FPR连接处taper的长度
    refractive_index: 芯层折射率
    L_in: 输入波导长度
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
                 W_taper_in: int or float = None,
                 L_taper_in: int or float = None,
                 W_taper_array: int or float = None,
                 L_taper_array: int or float = None,
                 L_in: int or float = None,
                 L_array: int or float = None,
                 refractive_index: float = None,
                 name: str = "awg_in",
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
        self.L_taper_in = L_taper_in or 0  # 赋默认值为 0
        self.W_taper_in = W_taper_in or 0  # 赋默认值为 0
        self.W_taper_array=W_taper_array or 0
        self.L_taper_array=L_taper_array or 0
        self.L_in=L_in
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
          self.W_taper_in, self.L_taper_in, self.W_taper_array, self.L_taper_array, self.L_in, self.L_array],
          grid_spacing=grid._grid.grid_spacing)
        #解压后的参数
        (self.x0, self.y0, self.z0, self.lam0_0, self.d0,
         self.delta_x0, self.w0, self.h0, self.L_FPR0, self.W_taper_in0,
         self.L_taper_in0, self.W_taper_array0, self.L_taper_array0, self.L_in0, self.L_array0) = converted_params

        self.add_roland_circle()  # 添加罗兰圆
        self.add_grating_arc()  # 添加光栅圆
        self.add_trapezoid()  # 添加连接罗兰圆和光栅圆的倒梯形
        if self.L_taper_in >0 and self.W_taper_in >0:  # 检查是否添加 taper
           self.add_taper_in()  # 添加连接输入波导和FPR区的taper_in
        self.add_waveguide_in()#添加输入波导
        if self.W_taper_array >0 and self.L_taper_array >0:  # 检查是否添加 taper_array
            self.add_taper_array_left()  # 添加连接阵列波导和FPR区左侧的taper_array
            self.add_taper_array_right()  # 添加连接阵列波导和FPR区右侧的taper_array
        self.add_waveguide_S1_left()  # 添加阵列波导直波导S1部分左侧波导
        self.add_waveguide_S1_right()  # 添加阵列波导直波导S1部分右侧波导
        # self.add_arc_and_waveguide_S2_left()  # 添加阵列波导左侧弯曲连接波导和直波导S2#todo:代码不完善
        # self.add_arc_and_waveguide_S2_right()  # 添加阵列波导右侧弯曲连接波导和直波导S2


    # 添加罗兰圆
    def add_roland_circle(self):
        angle0=bd.radians(-120)
        angle1=bd.radians(60)
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
               priority=self.priority)
        self._internal_objects.append(roland_circle)
    # 添加光栅圆
    def add_grating_arc(self):
          #修改后的代码：
          x2=self.x
          z2=int(self.z-self.L_FPR0/2)
          angle=(1.25*self.Ng)*self.d/self.L_FPR
          angle0= bd.pi / 2 - angle / 2#用阵列波导数目来控制光栅圆展开角度
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
    def add_trapezoid(self):
          #计算梯形的各个参数
          angle=(1.25*self.Ng)*self.d/self.L_FPR#光栅圆展开角度（圆心角）,弧度
          xlength_upper= 2 * self.L_FPR * bd.sin(angle / 2)#梯形上底
          xlength_lower=self.L_FPR/2#梯形下底边
          zlength = self.L_FPR * bd.cos(angle / 2) + (bd.sqrt(3) / 2 - 1) * self.L_FPR / 2#梯形的高

          #梯形的中心位置
          x_trapezoid=self.x
          y_trapezoid=self.y
          z_trapezoid=int((self.L_FPR0 * bd.cos(angle / 2) - self.L_FPR0 / 2 - (bd.sqrt(3) / 2) * self.L_FPR0 / 2) / 2 + self.z)
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
     # 添加连接输入波导和FPR区的taper_in
    def add_taper_in(self):
         x_taper_in = int(self.x)
         y_taper_in = int(self.y)
         z_taper_in = int(-self.L_FPR0 / 2 - self.L_taper_in0 / 2+self.z)
         taper_in = Taper(
              xlength_lower=self.w,
              xlength_upper=self.W_taper_in,
              zlength=self.L_taper_in,
              ylength=self.h,
              x=x_taper_in,
              y=y_taper_in,
              z=z_taper_in,
              refractive_index=self.refractive_index,
              name="taper_in",
              grid=self.grid,
              priority=self.priority
           )
         # 将taper对象添加到内部对象列表
         self._internal_objects.append(taper_in)

    # 添加输入波导
    def add_waveguide_in(self):
        x_waveguide_in = self.x
        y_waveguide_in = self.y
        z_waveguide_in = int(self.z-self.L_FPR0 / 2 - self.L_taper_in0 - self.L_in0 / 2)
        waveguide_in = Waveguide(
            xlength=self.w,
            ylength=self.h,
            zlength=self.L_in,
            x=x_waveguide_in,
            y=y_waveguide_in,
            z=z_waveguide_in,
            name="waveguide_in",
            refractive_index=self.refractive_index,
            grid=self.grid,
            priority=self.priority
            )
        # 将输入波导添加到内部对象列表
        self._internal_objects.append(waveguide_in )

    # 添加连接阵列波导和FPR区左侧的taper_array
    def add_taper_array_left(self):
        self.taper_array_left = []  # 用于存储多个 Taper 实例

        if self.Ng % 2 == 0:  # 如果 Ng 是偶数
           self.N_taper = int(self.Ng / 2)
           for n in range(1, self.N_taper+1):  # n 从 1 到 N_taper
               # 计算每个 taper 的坐标
               x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 / 2) * bd.sin(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * bd.cos(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

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
                  x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 / 2) * bd.sin(n * bd.radians(self.delta_angle_1)))
                  y_n = self.y
                  z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * bd.cos(n * bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

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
    def add_taper_array_right(self):
        self.taper_array_left = []  # 用于存储多个 Taper 实例

        if self.Ng % 2 == 0:  # 如果 Ng 是偶数
           self.N_taper = int(self.Ng / 2)
           for n in range(1, self.N_taper+1):  # n 从 1 到 N_taper
               # 计算每个 taper 的坐标
               x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 / 2) * bd.sin(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * bd.cos(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

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
                  x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 / 2) * bd.sin(n * bd.radians(self.delta_angle_1)))
                  y_n = self.y
                  z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 / 2) * bd.cos(n * bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2)  # 计算 z 坐标

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
    def add_waveguide_S1_left(self):
        self.waveguide_S1_left = []  # 用于存储所有波导实例

        if self.Ng % 2 == 0:  # 如果 Ng 是偶数
           self.N_taper = int(self.Ng / 2)
           for n in range(1, self.N_taper + 1):  # n 从 1 到 N_taper
               # 计算每个波导的坐标
               x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.sin(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.cos(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)

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
                 x_n = int(self.x - (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.sin(n * bd.radians(self.delta_angle_1)))
                 y_n = self.y
                 z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.cos(n * bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2)

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
    def add_waveguide_S1_right(self):
        self.waveguide_S1_right = []  # 用于存储右侧波导的实例

        if self.Ng % 2 == 0:  # 如果 Ng 是偶数
           self.N_taper = int(self.Ng / 2)
           for n in range(1, self.N_taper + 1):  # n 从 1 到 N_taper
               # 计算每个波导的坐标
               x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.sin(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)))
               y_n = self.y
               z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.cos(bd.radians(self.delta_angle_1 / 2 + (n - 1) * self.delta_angle_1)) - self.L_FPR0 / 2)

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
                x_n = int(self.x + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.sin(n * bd.radians(self.delta_angle_1)))
                y_n = self.y
                z_n = int(self.z + (self.L_FPR0 + self.L_taper_array0 + self.L_array0 / 2) * bd.cos(n * bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2)

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


    #添加阵列波导左侧弯曲连接波导和直波导S2
    #todo:没有区分奇数和偶数的阵列波导（下面只考虑了奇数的情况）
    #中间直波导S2写在这个模块
    def add_arc_and_waveguide_S2_left(self):
        self.arc_left = []
        self.waveguide_S2_left = []
        H0 = (self.L_array0 + self.L_taper_array0+self.L_FPR0) * bd.tan(bd.radians(self.delta_angle_1))#计算坐标
        H = (self.L_array+self.L_taper_array+ self.L_FPR) * bd.tan(bd.radians(self.delta_angle_1))#计算长度
        xC_0=self.x#中间直波导S2的坐标
        zC_0=int(self.z+(self.L_array0 +self.L_taper_array0+ self.L_FPR0)- self.L_FPR0 / 2)
        #中间直波导S2
        waveguide_S2_left0 = Waveguide(
                   x=xC_0,
                   y=self.y,
                   z=zC_0,
                   xlength=self.w,
                   ylength=self.h,
                   zlength=2*self.L_array,
                   name="waveguide_S2_left0",
                   refractive_index=self.refractive_index,
                   grid=self.grid,
                   priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(waveguide_S2_left0)
        #阵列波导左侧弯曲连接波导和直波导S2
        xA_1=self.x#左侧第一个歪曲波导的圆心坐标
        zA_1=int(self.z + (self.L_array0 +self.L_taper_array0+ self.L_FPR0) * bd.cos(bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2 + H0 * bd.sin(bd.radians(self.delta_angle_1)))
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
                    angle_phi=bd.pi,
                    angle_psi=bd.radians(self.delta_angle_1),
                    name="arc_left1",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(arc_left1)


        for n in range(2,self.N_taper+1):
            xB = int(self.x - (self.L_array0 +self.L_taper_array0+ self.L_FPR0) * bd.sin((n - 1) * bd.radians(self.delta_angle_1)))
            zB = int(self.z + (self.L_array0 +self.L_taper_array0+ self.L_FPR0) * bd.cos((n - 1) * bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2)
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
                    angle_phi=bd.pi,
                    angle_psi=bd.radians(n * self.delta_angle_1),
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
        H0 = (self.L_array0 + self.L_taper_array0+self.L_FPR0) * bd.tan(bd.radians(self.delta_angle_1))#计算坐标
        H = (self.L_array+self.L_taper_array+ self.L_FPR) * bd.tan(bd.radians(self.delta_angle_1))#计算长度
        xA_1=self.x
        zA_1=int(self.z + (self.L_array0 +self.L_taper_array0+ self.L_FPR0) * bd.cos(bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2 + H0 * bd.sin(bd.radians(self.delta_angle_1)))
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
                    angle_phi=-bd.radians(self.delta_angle_1),
                    angle_psi=bd.radians(self.delta_angle_1),
                    name="arc_right1",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
        # 添加到内部对象列表
        self._internal_objects.append(arc_right1)


        for n in range(2,self.N_taper+1):
            xB = int(self.x + (self.L_array0 +self.L_taper_array0+ self.L_FPR0) * bd.sin((n - 1) * bd.radians(self.delta_angle_1)))
            zB = int(self.z + (self.L_array0 +self.L_taper_array0+ self.L_FPR0) * bd.cos((n - 1) * bd.radians(self.delta_angle_1)) - self.L_FPR0 / 2)
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
                    angle_phi=-bd.radians(n * self.delta_angle_1),
                    angle_psi=bd.radians(n * self.delta_angle_1),
                    name=f"arc_right{n}",
                    refractive_index=self.refractive_index,
                    grid=self.grid,
                    priority=self.priority
             )
            self.arc_right.append(arc)
            # 同时添加到内部对象列表
            self._internal_objects.append(arc)



