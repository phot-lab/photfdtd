from waveguide import Waveguide
from ysplitter import Trapezoid


# import numpy as np
# import fdtd


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
        xlength=60,
        ylength=10,
        zlength=10,
        x=50,
        y=50,
        z=50,
        flag=1,
        width_wg=10,
        width_port=5,
        n=5,
        m=5,
        We=5,
        ln=10,
        lm=10,
        l_port=10,
        name="mmi",
        refractive_index=3.47,
        dn=1,
    ):
        Waveguide.__init__(self, xlength, ylength, zlength, x, y, z, flag, ylength, name, refractive_index)
        self.n = n
        self.m = m
        self.width_port = width_port
        self.width_wg = width_wg
        self.ln = ln
        self.lm = lm
        self.l_port = l_port
        self.We = We
        self.dn = dn

    def set_box(self):

        """设置多模波导"""

        waveguide0 = Waveguide(
            xlength=self.xlength,
            ylength=self.ylength,
            zlength=self.zlength,
            x=self.x,
            y=self.y,
            z=self.z,
            flag=self.flag,
            width=self.width,
            refractive_index=self.refractive_index,
            name="%s_waveguide0" % self.name,
        )
        result_waveguide0 = waveguide0.set_grid()
        return result_waveguide0

    def set_ports(self):

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

        result_in_port = [0] * self.n
        result_out_port = [0] * self.m
        result_in_wg = [0] * self.n
        result_out_wg = [0] * self.m

        for i in range(self.n):
            port = Trapezoid(
                xlength=self.l_port,
                ylength=self.width_port,
                zlength=self.zlength,
                x=x_port_in[i],
                y=y_port_in[i],
                z=self.z,
                flag=1,
                width=self.width_wg,
                name="port_input%d" % i,
                refractive_index=self.refractive_index,
            )
            wg = Waveguide(
                xlength=self.ln,
                ylength=self.width_wg,
                zlength=self.zlength,
                x=x_port_in[i] - self.ln,
                y=y_port_in[i] + int(self.width_port / 2 - self.width_wg / 2 + 0.5),
                z=self.z,
                flag=1,
                width=self.width_wg,
                name="waveguide_input%d" % i,
                refractive_index=self.refractive_index,
            )
            result_in_port[i] = port.set_grid()
            result_in_wg[i] = wg.set_grid()

        for i in range(self.m):
            port = Trapezoid(
                xlength=self.l_port,
                ylength=self.width_port,
                zlength=self.zlength,
                x=x_port_out[i],
                y=y_port_out[i],
                z=self.z,
                flag=-1,
                width=self.width_port,
                name="port_output%d" % i,
                refractive_index=self.refractive_index,
            )
            wg = Waveguide(
                xlength=self.lm,
                ylength=self.width_wg,
                zlength=self.zlength,
                x=x_port_out[i] + self.l_port,
                y=y_port_out[i] + int(self.width_port / 2 - self.width_wg / 2 + 0.5),
                z=self.z,
                flag=1,
                width=self.width_wg,
                name="waveguide_output%d" % i,
                refractive_index=self.refractive_index,
            )
            result_out_port[i] = port.set_grid()
            result_out_wg[i] = wg.set_grid()

        return result_in_port, result_out_port, result_in_wg, result_out_wg


if __name__ == "__main__":
    mmi = Mmi(
        xlength=175,
        ylength=36,
        zlength=1,
        We=37,
        x=50,
        y=10,
        z=1,
        flag=1,
        name="mmi",
        refractive_index=3.47,
        n=1,
        m=2,
        width_port=8,
        width_wg=2,
        l_port=10,
        ln=40,
        lm=5,
    )

    result0 = mmi.set_box()
    result_in, result_out, result_in_wg, result_out_wg = mmi.set_ports()

    print(result_in[0]["permittivity"][:, :, 0])
    # print(result0['permittivity'][:,:,0])
