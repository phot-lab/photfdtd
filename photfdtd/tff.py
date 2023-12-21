from .waveguide import Waveguide
import numpy as np


class TFF(Waveguide):
    """高折射率、低折射率交替排布的多层薄膜
    """

    def __init__(
            self,
            xlength: int = 71,
            ylength: int = 56,
            zlength: int = 20,
            x: int = 60,
            y: int = 40,
            z: int = 15,
            low_index: float = None,
            high_index: float = None,
            dl: int = None,
            dh: int = None,
            layers: int = None,
            name: str = "TFF",
            background_index: float = 1.0,
            axis: str = "z"
    ) -> None:
        x, y, z = np.full(layers, x), np.full(layers, y), np.full(layers, z)
        xlength_l, ylength_l, zlength_l = np.full(layers, xlength), np.full(layers, ylength), np.full(layers, zlength)
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
                                     int(z[i]), ylength, name + "_layer_" + str(i), high_index, background_index)

            else:
                layer[i] = Waveguide(xlength_l[i], ylength_l[i], zlength_l[i], int(x[i]), int(y[i]),
                                     int(z[i]), ylength, name + "_layer_" + str(i), low_index, background_index)

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
