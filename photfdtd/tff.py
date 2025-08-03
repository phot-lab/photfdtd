from .waveguide import Waveguide
import photfdtd.fdtd.backend as bd


class TFF(Waveguide):
    """
    薄膜
    """

    def __init__(
            self,
            xlength: int or float = 71,
            ylength: int or float = 56,
            zlength: int or float = 20,
            x: int or float = None,
            y: int or float = None,
            z: int or float = None,
            low_index: float = None,
            high_index: float = None,
            dl: int or float = None,
            dh: int or float = None,
            layers: int = None,
            axis: str = "z",
            name: str = "tf",
            grid=None,
            priority: int = 1
    ) -> None:
        """
        # TODO:不需要xlength, ylength, zlength这几个参数？
        高折射率、低折射率交替排布的多层薄膜
        @param xlength: xlength in total
        @param ylength: ylength in total
        @param zlength: zlength in total
        @param x, y, z: 在传播方向上取最底端坐标，非传播方向上取中心坐标.
        In the propagation direction, take the bottom coordinate,
        and in the non-propagation direction, take the center coordinate.
        @param low_index: lower refractive index
        @param high_index: higher refractive index
        @param dl: the thickness of the layer with low refractive index
        @param dh: the thickness of the layer with high refractive index
        @param layers: number of layers.
        @param axis: x, y, z, the propagation direction of the waveguide.
        @param name: the name of the waveguide.
        @param grid: photfdtd.Grid object, the grid to which the waveguide belongs.
        @param priority: the priority of the waveguide( high index indicates high priority).
        """
        xlength, x = grid._handle_unit([xlength, x], grid_spacing=grid._grid.grid_spacing_x)
        ylength, y = grid._handle_unit([ylength, y], grid_spacing=grid._grid.grid_spacing_y)
        zlength, z = grid._handle_unit([zlength, z], grid_spacing=grid._grid.grid_spacing_z)
        if x == None:
            # 如果没设置x，自动选仿真区域中心If x not set, choose the center of grid
            x = int(grid._grid_xlength / 2)
        if y == None:
            y = int(grid._grid_ylength / 2)
        if z == None:
            z = int(grid._grid_zlength / 2)

        x, y, z = bd.full(layers, x), bd.full(layers, y), bd.full(layers, z)
        xlength_l, ylength_l, zlength_l = bd.full(layers, xlength), bd.full(layers, ylength), bd.full(layers, zlength)
        for i in range(len(xlength_l)):
            xlength_l[i] = int(xlength_l[i])
        ylength_l = bd.astype(ylength_l, int)
        zlength_l = bd.astype(zlength_l, int)

        # xlength_l, ylength_l, zlength_l = int(xlength_l), int(ylength_l), int(zlength_l)
        if axis == "z":
            dl, dh = grid._handle_unit([dl, dh],grid_spacing=grid._grid.grid_spacing_z)
            z = self._calculate_position(z, layers, dl, dh)
            for i in range(layers):
                if i % 2 == 0:
                    zlength_l[i] = dh
                else:
                    zlength_l[i] = dl
        elif axis == "x":
            dl, dh = grid._handle_unit([dl, dh], grid_spacing=grid._grid.grid_spacing_x)
            x = self._calculate_position(x, layers, dl, dh)
            for i in range(layers):
                if i % 2 == 0:
                    xlength_l[i] = dh
                else:
                    xlength_l[i] = dl
        elif axis == "y":
            dl, dh = grid._handle_unit([dl, dh], grid_spacing=grid._grid.grid_spacing_y)
            y = self._calculate_position(y, layers, dl, dh)
            for i in range(layers):
                if i % 2 == 0:
                    ylength_l[i] = dh
                else:
                    ylength_l[i] = dl
        else:
            raise ValueError("parameter axis should be 'x', 'y' or 'z'")

        self._internal_objects = []
        layer = [0] * layers
        for i in range(layers):
            if i % 2 == 0:
                layer[i] = Waveguide(xlength_l[i], ylength_l[i], zlength_l[i], int(x[i]), int(y[i]),
                                     int(z[i]), ylength, name + "_layer_" + str(i), high_index, grid=grid, reset_xyz=True,
                                     priority=priority)

            else:
                layer[i] = Waveguide(xlength_l[i], ylength_l[i], zlength_l[i], int(x[i]), int(y[i]),
                                     int(z[i]), ylength, name + "_layer_" + str(i), low_index, grid=grid, reset_xyz=True,
                                     priority=priority)

        self._internal_objects.extend(layer)

    def _calculate_position(self, n, layers, dl, dh):
        for i in range(layers - 1):
            if i % 2 == 0:
                n[i + 1] = n[i] + dh
            else:
                n[i + 1] = n[i] + dl
        for i in range(layers):
            if i % 2 == 0:
                n[i] += int(dh / 2)
            else:
                n[i] += int(dl / 2)

        return n
