from .waveguide import Waveguide
import numpy as np


class TFF(Waveguide):
    """
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
            grid=None
    ) -> None:
        """
        # TODO:不需要xlength, ylength, zlength这几个参数？
        高折射率、低折射率交替排布的多层薄膜
        @param xlength:
        @param ylength:
        @param zlength:
        @param x, y, z: 在传播方向上取最底端坐标，非传播方向上取中心坐标
        @param low_index:
        @param high_index:
        @param dl:
        @param dh:
        @param layers:
        @param axis:
        @param name:
        @param grid:
        """
        xlength, ylength, zlength, dl, dh, x, y, z = grid._handle_unit([xlength, ylength, zlength, dl, dh, x, y, z],
                                                              grid_spacing=grid._grid.grid_spacing)

        x, y, z = np.full(layers, x), np.full(layers, y), np.full(layers, z)
        xlength_l, ylength_l, zlength_l = np.full(layers, xlength), np.full(layers, ylength), np.full(layers, zlength)
        for i in range(len(xlength_l)):
            xlength_l[i] = int(xlength_l[i])
        ylength_l = ylength_l.astype(int)
        zlength_l = zlength_l.astype(int)

        # xlength_l, ylength_l, zlength_l = int(xlength_l), int(ylength_l), int(zlength_l)
        if axis == "z":
            z = self._calculate_position(z, layers, dl, dh)
            for i in range(layers):
                if i % 2 == 0:
                    zlength_l[i] = dh
                else:
                    zlength_l[i] = dl
        elif axis == "x":
            x = self._calculate_position(x, layers, dl, dh)
            for i in range(layers):
                if i % 2 == 0:
                    xlength_l[i] = dh
                else:
                    xlength_l[i] = dl
        elif axis == "y":
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
                                     int(z[i]), ylength, name + "_layer_" + str(i), high_index, grid=grid, reset_xyz=True)

            else:
                layer[i] = Waveguide(xlength_l[i], ylength_l[i], zlength_l[i], int(x[i]), int(y[i]),
                                     int(z[i]), ylength, name + "_layer_" + str(i), low_index, grid=grid, reset_xyz=True)

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
