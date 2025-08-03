from .waveguide import Waveguide
from .ysplitter import Taper


class Mmi(Waveguide):
    """MMI，继承自Waveguide
    xlength: 多模波导x长度
    ylength: 厚度
    zlength: 多模波导z长度
    We: 有效宽度
    x,y,z: 中心坐标
    n: 输入数
    m：输出数
    width_port：端口宽度(端口是一个梯形，是一个Ysplitter.taper类对象)
    width_wg:单模波导宽度
    ln：输入波导z长度
    lm：输出波导z长度
    l_port: 端口长度
    refractive_index: 折射率
    background_index: 环境折射率
    priority: the priority of the waveguide( high index indicates high priority).
    """

    # FIXME: 矩形波导与MMI之间有缝隙
    def __init__(
            self,
            xlength: int or float = 71,
            ylength: int or float = 56,
            zlength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width_wg: int or float = None,
            width_port: int or float = None,
            n: int = 1,
            m: int = 2,
            We: int or float = None,
            ln: int or float = 20,
            lm: int or float = 20,
            l_port: int or float = 0,
            name: str = "mmi",
            refractive_index: float = 3.47,
            grid=None,
            priority: int = 1
    ) -> None:
        # TODO: 如果没有给定We，则算出We
        xlength, width_wg, width_port, We = grid._handle_unit(
            [xlength, width_wg, width_port, We], grid_spacing=grid._grid.grid_spacing_x)
        ylength = grid._handle_unit([ylength], grid_spacing=grid._grid.grid_spacing_y)[0]
        zlength, ln, lm, l_port = grid._handle_unit(
            [zlength, ln, lm, l_port], grid_spacing=grid._grid.grid_spacing_z)
        self.n = n
        self.m = m
        if not width_port:
            self.width_port = width_wg
        else:
            self.width_port = width_port
        self.width_wg = width_wg
        self.ln = ln
        self.lm = lm
        self.l_port = l_port
        if not We:
            self.We = xlength
        else:
            self.We = We

        super().__init__(xlength, ylength, zlength, x, y, z,
                         ylength, name, refractive_index, grid=grid, reset_xyz=False, priority=priority)

    def _set_objects(self):
        self._set_box()
        self._set_ports()

        self._internal_objects = [self.waveguide]
        if self.l_port != 0:
            self._internal_objects.extend(self.ports_in)
            self._internal_objects.extend(self.ports_out)
        self._internal_objects.extend(self.waveguides_in)
        self._internal_objects.extend(self.waveguides_out)

    def _set_box(self):

        """设置多模波导"""

        waveguide = Waveguide(
            xlength=self.xlength,  # 防止空隙
            ylength=self.ylength,
            zlength=self.zlength + 2,
            x=self.x,
            y=self.y,
            z=self.z,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_Box" % self.name,
            grid=self.grid
        )
        self.waveguide = waveguide

    def _set_ports(self):

        """输入及输出端口"""

        z_port_in = [self.z - int(self.zlength / 2 + self.l_port / 2)] * self.n
        z_port_out = [self.z + int(self.zlength / 2 + self.l_port / 2)] * self.m
        x_port_out = [0] * self.m
        x_port_in = [0] * self.n

        if self.n == 1:

            x_port_in[0] = self.x + int(self.xlength / 2 - self.width_port / 2)

            # for i in range(self.m):
            #     i += 1
            #     x_port_out[i - 1] = (
            #             self.x
            #             + int(self.xlength / 2 - self.width_port / 2)
            #             + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We)
            #     )

        if self.n == 2:
            """2*m"""
            x_port_in[0] = self.x + int(self.xlength / 2 - self.We / 6 - self.width_port / 2)
            x_port_in[1] = self.x + int(self.xlength / 2 + self.We / 6 - self.width_port / 2)

            # for i in range(self.m):
            #     i += 1
            #     x_port_out[i - 1] = (
            #             self.x
            #             + int(self.xlength / 2 - self.width_port / 2)
            #             + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We)
            #     )

        x_port_in = [x - int(self.xlength / 2 - self.width_port / 2) for x in x_port_in]


        if self.n > 2:
            """n*m"""
            for i in range(self.n):
                x_port_in[i] = self.x - int(self.xlength / 2) + int(self.xlength / 2 / self.n) + int(
                    self.xlength / self.n) * i
            # for i in range(self.m):
            #     x_port_out[i] = self.x - int(self.xlength / 2) + int(self.xlength / 2 / self.m) + int(
            #         self.xlength / self.m) * i
            # for i in range(self.n):
            #     i += 1
            #     x_port_in[i - 1] = (
            #             self.x
            #             + int(self.xlength / 2 - self.width_port / 2)
            #             + int(((2 * i - (self.n + 1)) / (2 * self.n)) * self.We)
            #     )
        for i in range(self.m):
            i += 1
            x_port_out[i - 1] = (
                    self.x
                    + int(self.xlength / 2 - self.width_port / 2)
                    + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We)
            )
        x_port_out = [x - int(self.xlength / 2 - self.width_port / 2) for x in x_port_out]

        ports_in = [0] * self.n
        ports_out = [0] * self.m
        waveguides_in = [0] * self.n
        waveguides_out = [0] * self.m

        for i in range(self.n):
            if self.l_port:
                port = Taper(xlength=self.width_port, width=self.width_wg, ylength=self.ylength, zlength=self.l_port,
                             x=x_port_in[i], y=self.y, z=z_port_in[i], name="%s_port_input%d" % (self.name, i),
                             refractive_index=self.refractive_index, grid=self.grid, priority=self.priority)
                ports_in[i] = port
            wg = Waveguide(
                xlength=self.width_wg,
                ylength=self.ylength,
                zlength=self.ln,
                x=x_port_in[i],
                y=self.y,
                z=z_port_in[i] - int(self.ln / 2 + self.l_port / 2),
                width=self.width_wg,
                name="%s_waveguide_input%d" % (self.name, i),
                refractive_index=self.refractive_index,
                grid=self.grid,
                priority=self.priority
            )

            waveguides_in[i] = wg

        for i in range(self.m):
            if self.l_port:
                port = Taper(xlength_upper=self.width_wg, xlength_lower=self.width_port, width=self.width_wg,
                             ylength=self.ylength, zlength=self.l_port, x=x_port_out[i], y=self.y, z=z_port_out[i],
                             name="%s_port_output%d" % (self.name, i), refractive_index=self.refractive_index,
                             grid=self.grid, priority=self.priority)
                ports_out[i] = port
            wg = Waveguide(
                xlength=self.width_wg,
                ylength=self.ylength,
                zlength=self.lm,
                x=x_port_out[i],
                y=self.y,
                z=z_port_out[i] + int(self.lm / 2 + self.l_port / 2),
                width=self.width_wg,
                name="%s_waveguide_output%d" % (self.name, i),
                refractive_index=self.refractive_index,
                grid=self.grid,
                priority=self.priority
            )

            waveguides_out[i] = wg

        if self.l_port:
            self.ports_in = ports_in
            self.ports_out = ports_out
        self.waveguides_in = waveguides_in
        self.waveguides_out = waveguides_out
