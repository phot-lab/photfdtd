from .waveguide import Waveguide
import photfdtd.fdtd.backend as bd


class Sbend(Waveguide):
    """
    s波导代码，继承自waveguide
    xlength: x跨度，+-号控制波导方向
    ylength: 厚度
    zlength: 长度
    x,y,z: 中心坐标 (若希望x,y,z为波导起始位置，把center_postion设为False)
    width：波导宽度
    refractive_index: 折射率
    grid: grid
    priority: the priority of the waveguide( high index indicates high priority).
    """
    # TODO: 像Rsoft里那样设置sbend。The settings of Sbend should be like that in Rsoft.
    def __init__(
            self,
            xlength: int or float = None,
            ylength: int or float = None,
            zlength: int or float = None,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            width: int or float = 20,
            name: str = "sbend",
            refractive_index: float = 3.47,
            grid=None,
            center_postion: bool = True,
            direction: int = None,
            priority: int = 1
    ) -> None:
        xlength, width, x= grid._handle_unit([xlength, width, x], grid_spacing=grid._grid.grid_spacing_x)
        ylength, y = grid._handle_unit([ylength, y], grid_spacing=grid._grid.grid_spacing_y)
        zlength, z = grid._handle_unit([zlength, z], grid_spacing=grid._grid.grid_spacing_z)
        if not center_postion:
            x, y, z = x + xlength / 2 - width / 2, y, z + zlength / 2
        if not direction:
            if xlength < 0:
                direction = -1
            else:
                direction = 1
        self.direction = direction
        super().__init__(abs(xlength), ylength, zlength, x, y, z, width, name, refractive_index, grid=grid, priority=priority)

    def _compute_permittivity(self):
        """
        """
        z = bd.linspace(0, self.zlength, self.zlength)
        x = bd.linspace(0, self.xlength, self.xlength)
        Z, X = bd.meshgrid(z, x, indexing="ij")  # indexing = 'ij'很重要
        m = bd.zeros((self.xlength, self.ylength, self.zlength))

        if self.direction == 1:
            # direction=1, 波导方向从左下到右上
            m1 = (
                    X
                    <= 0.5 * (self.xlength - self.width) * bd.sin((Z / self.zlength - 0.5) * bd.pi)
                    + int(self.width / 2 + 0.5)
                    + self.xlength / 2
            )
            # 上下翻转
            m2 = bd.flipud(m1)
            # 左右翻转
            m2 = bd.fliplr(m2)

            # m2 = (
            #         X
            #         <= 0.5 * (self.xlength - self.width) * bd.sin((Z / self.zlength - 0.5) * bd.pi)
            #         - int(self.width / 2 + 0.5)
            #         + self.xlength / 2
            # )

            # m2 = (
            #     X
            #     >= 0.5 * (self.xlength - self.width) * bd.sin((Z / self.zlength - 0.5) * bd.pi)
            #     - self.width / 2
            #     + self.xlength / 2
            # )
        elif self.direction == -1:
            # direction=-1, 波导方向从左上到右下
            m1 = (
                    X
                    <= -0.5 * (self.xlength - self.width) * bd.sin((Z / self.zlength - 0.5) * bd.pi)
                    + int(self.width / 2 + 0.5)
                    + self.xlength / 2
            )
            # 上下翻转
            m2 = bd.flipud(m1)
            # 左右翻转
            m2 = bd.fliplr(m2)
            # m2 = (
            #     X
            #     >= -0.5 * (self.xlength - self.width) * bd.sin((Z / self.zlength - 0.5) * bd.pi)
            #     - self.width / 2
            #     + self.xlength / 2
            # )
        else:
            raise RuntimeError("Unknown direction")

        for i in range(self.zlength):
            for j in range(self.xlength):
                if m1[i, j] == m2[i, j]:
                    m[j, :, i] = True

        permittivity = bd.ones((self.xlength, self.ylength, self.zlength))
        permittivity += m[:, :] * (self.refractive_index ** 2 - 1)
        permittivity += (1 - m[:, :]) * (self.background_index ** 2 - 1)

        self.permittivity = permittivity
