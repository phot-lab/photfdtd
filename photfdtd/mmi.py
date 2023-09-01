from .waveguide import Waveguide
from .ysplitter import Taper
import photfdtd.fdtd as fdtd


class Mmi(Waveguide):
    """MMI，继承自Waveguide
    xlength: 多模波导区域x方向宽度
    ylength: 多模波导区域y方向宽度
    zlength: 多模波导区域z方向宽度，通常也是波导高度
    We: 多模波导有效宽度
    x,y,z: 多模波导位置坐标（通常是矩形区域最靠近原点的点）
    n: 输入波导数
    m：输出波导数
    width_port：端口宽度(端口是一个梯形，是一个Ysplitter.taper类对象)
    width_wg:单模波导宽度
    ln：输入波导长度（x方向长度）
    lm：输出波导长度（x方向长度）
    l_port: 端口长度
    refractive_index:折射率
    background_index: 环境折射率
    """

    def __init__(
            self,
            xlength: int = 71,
            ylength: int = 56,
            zlength: int = 20,
            x: int = 60,
            y: int = 40,
            z: int = 15,
            width_wg: int = 20,
            width_port: int = 25,
            n: int = 1,
            m: int = 2,
            We: int = 56,
            ln: int = 20,
            lm: int = 20,
            l_port: int = 0,
            name: str = "mmi",
            refractive_index: float = 3.47,
            background_index: float = 1.0
    ) -> None:
        # TODO: 如果没有给定We，则算出We
        # TODO: 光路沿ｙ方向？
        self.n = n
        self.m = m
        self.width_port = width_port
        self.width_wg = width_wg
        self.ln = ln
        self.lm = lm
        self.l_port = l_port
        self.We = We

        super().__init__(xlength, ylength, zlength, x + int(xlength / 2), y + int(ylength / 2), z + int(zlength / 2),
                         ylength, name, refractive_index, background_index)

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
            xlength=self.xlength,
            ylength=self.ylength,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_waveguide0" % self.name,
            background_index=self.background_index
        )
        self.waveguide = waveguide

    def _set_ports(self):

        """输入及输出端口"""

        x_port_in = [self.x - int(self.xlength / 2 + self.l_port / 2)] * self.n
        x_port_out = [self.x + int(self.xlength / 2 + self.l_port / 2)] * self.m
        y_port_out = [0] * self.m
        y_port_in = [0] * self.n

        if self.n == 1:

            y_port_in[0] = self.y + int(self.ylength / 2 - self.width_port / 2)

            for i in range(self.m):
                i += 1
                y_port_out[i - 1] = (
                        self.y
                        + int(self.ylength / 2 - self.width_port / 2)
                        + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We)
                )

        if self.n == 2:
            """2*m"""
            y_port_in[0] = self.y + int(self.ylength / 2 - self.We / 6 - self.width_port / 2)
            y_port_in[1] = self.y + int(self.ylength / 2 + self.We / 6 - self.width_port / 2)

            for i in range(self.m):
                i += 1
                y_port_out[i - 1] = (
                        self.y
                        + int(self.ylength / 2 - self.width_port / 2)
                        + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We)
                )

        y_port_in = [x - int(self.ylength / 2 - self.width_port / 2) for x in y_port_in]
        y_port_out = [x - int(self.ylength / 2 - self.width_port / 2) for x in y_port_out]

        if self.n > 2:
            """n*m"""
            for i in range(self.n):
                y_port_in[i] = self.y - int(self.ylength / 2) + int(self.ylength / 2 / self.n) + int(
                    self.ylength / self.n) * i
            for i in range(self.m):
                y_port_out[i] = self.y - int(self.ylength / 2) + int(self.ylength / 2 / self.m) + int(
                    self.ylength / self.m) * i

        ports_in = [0] * self.n
        ports_out = [0] * self.m
        waveguides_in = [0] * self.n
        waveguides_out = [0] * self.m

        for i in range(self.n):
            # 23.3.22: 由于器件不能重名，更改了下面name的表达式

            port = Taper(
                xlength=self.l_port,
                ylength=self.width_port,
                zlength=self.zlength,
                x=x_port_in[i],
                y=y_port_in[i],
                z=self.z,
                direction=1,
                width=self.width_wg,
                name="%s_port_input%d" % (self.name, i),
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            wg = Waveguide(
                xlength=self.ln,
                ylength=self.width_wg,
                zlength=self.zlength,
                x=x_port_in[i] - int(self.ln / 2 + self.l_port / 2),
                y=y_port_in[i],
                z=self.z,
                width=self.width_wg,
                name="%s_waveguide_input%d" % (self.name, i),
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            ports_in[i] = port
            waveguides_in[i] = wg

        for i in range(self.m):
            port = Taper(
                xlength=self.l_port,
                ylength=self.width_port,
                zlength=self.zlength,
                x=x_port_out[i],
                y=y_port_out[i],
                z=self.z,
                direction=-1,
                width=self.width_wg,
                name="%s_port_output%d" % (self.name, i),
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            wg = Waveguide(
                xlength=self.lm,
                ylength=self.width_wg,
                zlength=self.zlength,
                x=x_port_out[i] + int(self.ln / 2 + self.l_port / 2),
                y=y_port_out[i],
                z=self.z,
                width=self.width_wg,
                name="%s_waveguide_output%d" % (self.name, i),
                refractive_index=self.refractive_index,
                background_index=self.background_index
            )
            ports_out[i] = port
            waveguides_out[i] = wg

        self.ports_in = ports_in
        self.ports_out = ports_out
        self.waveguides_in = waveguides_in
        self.waveguides_out = waveguides_out
