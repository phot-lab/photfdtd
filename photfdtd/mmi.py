from .waveguide import Waveguide
from .ysplitter import Trapezoid
import fdtd


class Mmi(Waveguide):
    """MMI，继承自Waveguide
    xlength: 多模波导区域x方向宽度
    ylength: 多模波导区域y方向宽度
    zlength: 多模波导区域z方向宽度，通常也是波导高度
    We: 多模波导有效宽度
    x,y,z: 多模波导位置坐标（通常是矩形区域最靠近原点的点）
    n: 输入波导数
    m：输出波导数
    width_port：端口宽度(端口是一个梯形，是一个Ysplitter.trapezoid类对象)
    width_wg:单模波导宽度
    ln：输入波导长度（x方向宽度）
    lm：输入波导长度（x方向宽度）
    dn: n*n MMI中，一组（一对）波导间的间距
    l_port: 端口长度
    refractive_index:折射率
    """

    def __init__(
        self,
        xlength: int = 60,
        ylength: int = 10,
        zlength: int = 10,
        x: int = 50,
        y: int = 50,
        z: int = 50,
        direction: int = 1,
        width_wg: int = 10,
        width_port: int = 5,
        n: int = 5,
        m: int = 5,
        We: int = 5,
        ln: int = 10,
        lm: int = 10,
        l_port: int = 10,
        name: str = "mmi",
        refractive_index: float = 3.47,
        dn: int = 1,
    ):
        self.direction = direction
        self.n = n
        self.m = m
        self.width_port = width_port
        self.width_wg = width_wg
        self.ln = ln
        self.lm = lm
        self.l_port = l_port
        self.We = We
        self.dn = dn
        super().__init__(xlength, ylength, zlength, x, y, z, ylength, name, refractive_index)

    def _set_objects(self):
        self._set_box()
        self._set_ports()

        self._internal_objects = [self.waveguide]
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
            name=f"{self.name}_waveguide0",
        )
        self.waveguide = waveguide

    def _set_ports(self):

        """输入及输出端口"""

        x_port_in = [self.x - self.l_port] * self.n
        x_port_out = [self.x + self.xlength] * self.m
        y_port_out = [0] * self.m
        y_port_in = [0] * self.n

        if self.n == 1:

            y_port_in[0] = self.y + int(self.ylength / 2 - self.width_port / 2 + 0.5)

            for i in range(self.m):
                i += 1
                y_port_out[i - 1] = (
                    self.y
                    + int(self.ylength / 2 - self.width_port / 2 + 0.5)
                    + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We + 0.5)
                )

        if self.n == 2:
            """2*m"""
            y_port_in[0] = self.y + int(self.ylength / 2 - self.We / 6 - self.width_port / 2 + 0.5)
            y_port_in[1] = self.y + int(self.ylength / 2 + self.We / 6 - self.width_port / 2 + 0.5)

            for i in range(self.m):
                i += 1
                y_port_out[i - 1] = (
                    self.y
                    + int(self.ylength / 2 - self.width_port / 2 + 0.5)
                    + int(((2 * i - (self.m + 1)) / (2 * self.m)) * self.We + 0.5)
                )

        if self.n > 2:
            """n*n"""
            if self.n % 2 == 0:  # n为偶 参考论文：bachmann 1994
                for i in range(int(self.n / 2)):
                    y_port_in[i * 2] = int(
                        self.y
                        + self.ylength
                        + self.dn / 2
                        - self.ylength / self.n
                        - i * 2 * self.ylength / self.n
                        + 0.5
                    )
                    y_port_in[i * 2 + 1] = y_port_in[i * 2] - self.dn - self.width_port
                    y_port_out[i * 2] = int(
                        self.y + self.ylength / self.n - self.dn / 2 - self.width_port + i * 2 * self.ylength / self.n
                    )
                    y_port_out[i * 2 + 1] = y_port_out[i * 2] + self.dn + self.width_port
            else:  # n为奇

                y_port_in = [0] * self.n

                for i in range(int(self.n / 2 - 0.5)):
                    y_port_in[i * 2] = int(
                        self.x + self.ylength + self.dn / 2 - self.ylength / self.n - i * 2 * self.ylength / self.n
                    )
                    y_port_in[i * 2 + 1] = y_port_in[i * 2] - self.dn - self.width_port
                    y_port_out[i * 2] = int(
                        self.x + self.ylength / self.n - self.dn / 2 - self.width_port + i * 2 * self.ylength / self.n
                    )
                    y_port_out[i * 2 + 1] = y_port_out[i * 2] + self.dn + self.width_port
                y_port_in[self.n - 1] = (
                    y_port_in[self.n - 2] - int(self.ylength * 2 / self.n) + self.dn + self.width_port
                )
                y_port_out[self.n - 1] = (
                    y_port_in[self.n - 2] + int(self.ylength * 2 / self.n) - self.dn - self.width_port
                )

        ports_in = [0] * self.n
        ports_out = [0] * self.m
        waveguides_in = [0] * self.n
        waveguides_out = [0] * self.m

        for i in range(self.n):
            port = Trapezoid(
                xlength=self.l_port,
                ylength=self.width_port,
                zlength=self.zlength,
                x=x_port_in[i],
                y=y_port_in[i],
                z=self.z,
                direction=1,
                width=self.width_wg,
                name=f"{self.name}_port_input{i}",
                refractive_index=self.refractive_index,
            )
            wg = Waveguide(
                xlength=self.ln,
                ylength=self.width_wg,
                zlength=self.zlength,
                x=x_port_in[i] - self.ln,
                y=y_port_in[i] + int(self.width_port / 2 - self.width_wg / 2 + 0.5),
                z=self.z,
                width=self.width_wg,
                name=f"{self.name}_waveguide_input{i}",
                refractive_index=self.refractive_index,
            )
            ports_in[i] = port
            waveguides_in[i] = wg

        for i in range(self.m):
            port = Trapezoid(
                xlength=self.l_port,
                ylength=self.width_port,
                zlength=self.zlength,
                x=x_port_out[i],
                y=y_port_out[i],
                z=self.z,
                direction=-1,
                width=self.width_port,
                name=f"{self.name}_port_output{i}",
                refractive_index=self.refractive_index,
            )
            wg = Waveguide(
                xlength=self.lm,
                ylength=self.width_wg,
                zlength=self.zlength,
                x=x_port_out[i] + self.l_port,
                y=y_port_out[i] + int(self.width_port / 2 - self.width_wg / 2 + 0.5),
                z=self.z,
                width=self.width_wg,
                name=f"{self.name}_waveguide_output{i}",
                refractive_index=self.refractive_index,
            )
            ports_out[i] = port
            waveguides_out[i] = wg

        self.ports_in = ports_in
        self.ports_out = ports_out
        self.waveguides_in = waveguides_in
        self.waveguides_out = waveguides_out
