""" Sources are objects that inject the fields into the grid.

Available sources:

- PointSource
- LineSource

"""
## Imports

# other
from math import pi, sin

# typing
from .typing_ import Tuple, Number, ListOrSlice, List
from numpy import ndarray

# relatvie
from .grid import Grid
from .backend import backend as bd
from .waveforms import *
from .detectors import CurrentDetector
from .conversions import *


## PointSource class
class PointSource:
    """A source placed at a single point (grid cell) in the grid"""

    # TODO: 为点光源和面光源加上gaussian waveform

    def __init__(
            self,
            period: Number = 15,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            name: str = None,
            pulse_type: str = "None",
            cycle: int = 5,
            hanning_dt: float = 10.0,
            pulse_length: float = 39e-15,
            offset: float = 112e-15,
            polarization: str = "z",
            real_EH_unit: bool = True
    ):
        """Create a LineSource with a gaussian profile

        Args:
            period: The period of the source. The period can be specified
                as integer [timesteps] or as float [seconds]
            amplitude: The electric field amplitude in simulation units
            phase_shift: The phase offset of the source.
            name: name of the source.
            hanning_dt: timestep used for Hanning window waveform width (optional).
            waveform: "plane"代表平面波，“gaussian”代表高斯波形
            cycle: cycles for Hanning window waveform.
            pulse_length: 脉宽(对于高斯脉冲：半高全宽)单位s
            offset: 脉冲中心时间 修改于23.5.14 单位s
            pulse_type: "gaussian"代表高斯脉冲 "hanning"代表汉宁脉冲 "none"或者其他任何输入代表不使用脉冲
            polarization: 电场偏振方向 "x" "y" "z"
            real_EH_unit: use real unit for E and H?
        """
        self.grid = None
        self.period = period
        self.amplitude = amplitude
        if real_EH_unit:
            self.sim_amplitude = worldE_to_simE(amplitude)
        else:
            self.sim_amplitude = amplitude
        self.phase_shift = phase_shift
        self.name = name
        self.pulse_type = pulse_type
        self.cycle = cycle
        self.frequency = 1.0 / period
        self.hanning_dt = hanning_dt if hanning_dt is not None else 0.5 / self.frequency
        self.offset = offset
        self.pulse_length = pulse_length
        self.polarization = polarization

    def _register_grid(self, grid: Grid, x: Number, y: Number, z: Number):
        """Register a grid for the source.

        Args:
            grid: the grid to place the source into.
            x: The x-location of the source in the grid
            y: The y-location of the source in the grid
            z: The z-location of the source in the grid

        Note:
            As its name suggests, this source is a POINT source.
            Hence it should be placed at a single coordinate tuple
            int the grid.
        """
        self.grid = grid
        self.grid.sources.append(self)
        if self.name is not None:
            if not hasattr(grid, self.name):
                setattr(grid, self.name, self)
            else:
                raise ValueError(
                    f"The grid already has an attribute with name {self.name}"
                )

        try:
            (x,), (y,), (z,) = x, y, z
        except (TypeError, ValueError):
            raise ValueError("a point source should be placed on a single grid cell.")
        self.x, self.y, self.z = grid._handle_tuple((x, y, z))
        self.period = grid._handle_time(self.period)

    def update_E(self):
        """Add the source to the electric field"""
        q = self.grid.time_steps_passed
        # if pulse = hanning
        if self.pulse_type == "hanning":
            t1 = int(2 * pi / (self.frequency * self.hanning_dt / self.cycle))
            if q < t1:
                src = self.sim_amplitude * hanning(
                    self.frequency, q * self.hanning_dt, self.cycle
                )
            else:
                # src = - self.grid.E[self.x, self.y, self.z, 2]
                src = 0
        elif self.pulse_type == "gaussian":
            src = self.sim_amplitude * pulse_oscillation(frequency=self.frequency, t=q * self.grid.time_step,
                                    pulselength=self.pulse_length, offset=self.offset)

        # if not pulse
        else:
            src = self.sim_amplitude * sin(2 * pi * q / self.period + self.phase_shift)
        self._Epol = 'xyz'.index(self.polarization)
        # str.index(a)方法给出str中a的所在位置
        # self.grid.E[self.x, self.y, self.z, self._Epol] += src
        # 变成硬源试试
        self.grid.E[self.x, self.y, self.z, self._Epol] = src
    def update_H(self):
        """Add the source to the magnetic field"""

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(period={self.period}, "
            f"amplitude={self.amplitude}, phase_shift={self.phase_shift}, "
            f"name={repr(self.name)})"
        )

    def __str__(self):
        s = "    " + repr(self) + "\n"
        x = f"{self.x}"
        y = f"{self.y}"
        z = f"{self.z}"
        s += f"        @ x={x}, y={y}, z={z}\n"
        return s

    @property
    def bandwidth(self):
        if self.pulse_type is not None:
            return bandwidth(self.pulse_length)
        else:
            return 25e12


## LineSource class
class LineSource:
    """A source along a line in the FDTD grid"""

    def __init__(
            self,
            period: Number = 15,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            name: str = None,
            waveform: str = "plane",
            polarization: str = "z",
            pulse_type: str = None,
            pulse_length: float = 39e-15,
            offset: float = 112e-15,
            cycle: int = 5,
            real_EH_unit: bool = True
    ):
        """Create a LineSource with a gaussian profile
        Args:
            period: The period of the source. The period can be specified
                as integer [timesteps] or as float [seconds]
            amplitude: The amplitude of the source in simulation units
            phase_shift: The phase offset of the source.
            waveform: "plane"代表平面波，“gaussian”代表高斯波形
            pulse_type: "gaussian"代表高斯脉冲 "hanning"代表汉宁脉冲 "none"或者其他任何输入代表不使用脉冲
            pulse_length: 脉宽(对于高斯脉冲：半高全宽*sqrt(2))单位s
            offset: 脉冲中心时间 修改于23.5.14 单位s
            cycle: cycles for Hanning window pulse.
            polarization: 电场偏振方向 "x" "y" "z"
        """
        self.grid = None
        self.period = period
        self.amplitude = amplitude
        if real_EH_unit:
            self.sim_amplitude = worldE_to_simE(amplitude)
        else:
            self.sim_amplitude = amplitude
        self.phase_shift = phase_shift
        self.name = name
        self.waveform = waveform
        if pulse_type != "gaussian" and pulse_type != "hanning":
            self.pulse_type = None
        else:
            self.pulse_type = pulse_type
        self.cycle = cycle
        self.frequency = 1.0 / period
        self.pulse_length = pulse_length
        self.offset = offset
        self.polarization = polarization

    def _register_grid(
            self, grid: Grid, x: ListOrSlice, y: ListOrSlice, z: ListOrSlice
    ):
        """Register a grid for the source.

        Args:
            grid: the grid to place the source into.
            x: The x-location of the source in the grid
            y: The y-location of the source in the grid
            z: The z-location of the source in the grid

        Note:
            As its name suggests, this source is a LINE source.
            Hence the source spans the diagonal of the cube
            defined by the slices in the grid.
        """
        self.grid = grid
        self.grid.sources.append(self)
        if self.name is not None:
            if not hasattr(grid, self.name):
                setattr(grid, self.name, self)
            else:
                raise ValueError(
                    f"The grid already has an attribute with name {self.name}"
                )

        self.x, self.y, self.z = self._handle_slices(x, y, z)

        self.period = grid._handle_time(self.period)

        L = len(self.x)
        vect = bd.array(
            (bd.array(self.x) - self.x[L // 2]) ** 2
            + (bd.array(self.y) - self.y[L // 2]) ** 2
            + (bd.array(self.z) - self.z[L // 2]) ** 2,
            bd.float,
        )  # vect：这是一个包含了各个点到中心点的距离平方的三维数组。它通过计算每个点到中心点的距离平方的和来创建。
        self.profile = bd.ones(tuple(vect.shape))
        if self.waveform == "gaussian":
            # floris的源代码是这么写的，这其实不是一个标准的高斯分布，因为它计算了距离的二次平方。一个标准的高斯分布应该是：
            # self.profile = bd.exp(-vect / (2 * (0.5 * vect.max()) ** 2))
            self.profile = bd.exp(-(vect ** 2) / (2 * (0.5 * vect.max()) ** 2))  # 这是一个高斯分布
        self.profile /= self.profile.max()  # 在计算高斯分布之后，代码将其归一化，确保分布的最大值为1。
        self.profile *= self.sim_amplitude

    def _handle_slices(
            self, x: ListOrSlice, y: ListOrSlice, z: ListOrSlice
    ) -> Tuple[List, List, List]:
        """Convert slices in the grid to lists

        This is necessary to make the source span the diagonal of the volume
        defined by the slices.

        Args:
            x: The x-location of the volume in the grid
            y: The y-location of the volume in the grid
            z: The z-location of the volume in the grid

        Returns:
            x, y, z: the x, y and z coordinates of the source as lists

        """

        # if list-indices were chosen:
        if isinstance(x, list) and isinstance(y, list) and isinstance(z, list):
            if len(x) != len(y) or len(y) != len(z) or len(z) != len(x):
                raise IndexError(
                    "sources require grid to be indexed with slices or equal length list-indices"
                )
            x = [self.grid._handle_distance(_x, "x") for _x in x]
            y = [self.grid._handle_distance(_y, "y") for _y in y]
            z = [self.grid._handle_distance(_z, "z") for _z in z]
            return x, y, z

        # if a combination of list-indices and slices were chosen,
        # convert the list-indices to slices.
        # TODO: maybe issue a warning here?
        if isinstance(x, list):
            x = slice(
                self.grid._handle_distance(x[0], "x"),
                self.grid._handle_distance(x[-1], "x"),
                None,
            )
        if isinstance(y, list):
            y = slice(
                self.grid._handle_distance(y[0], "y"),
                self.grid._handle_distance(y[-1], "y"),
                None,
            )
        if isinstance(z, list):
            z = slice(
                self.grid._handle_distance(z[0], "z"),
                self.grid._handle_distance(z[-1], "z"),
                None,
            )

        # if we get here, we can assume slices:
        x0 = self.grid._handle_distance(x.start if x.start is not None else 0, "x")
        y0 = self.grid._handle_distance(y.start if y.start is not None else 0, "y")
        z0 = self.grid._handle_distance(z.start if z.start is not None else 0, "z")
        x1 = self.grid._handle_distance(x.stop if x.stop is not None else self.grid.Nx, "x")
        y1 = self.grid._handle_distance(y.stop if y.stop is not None else self.grid.Ny, "y")
        z1 = self.grid._handle_distance(z.stop if z.stop is not None else self.grid.Nz, "z")

        # we can now convert these coordinates into index lists
        m = max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
        if m < 2:
            raise ValueError("a LineSource should consist of at least two gridpoints")
        x = [v.item() for v in bd.array(bd.linspace(x0, x1, m, endpoint=False), bd.int)]
        y = [v.item() for v in bd.array(bd.linspace(y0, y1, m, endpoint=False), bd.int)]
        z = [v.item() for v in bd.array(bd.linspace(z0, z1, m, endpoint=False), bd.int)]

        return x, y, z

    @property
    def bandwidth(self):
        if self.pulse_type is not None:
            return bandwidth(self.pulse_length)
        else:
            return 25e12

    def update_E(self):
        """Add the source to the electric field"""
        q = self.grid.time_steps_passed
        # if pulse = "hanning"
        if self.pulse_type == "hanning":
            t1 = int(2 * pi / (self.frequency * self.pulse_length / self.cycle))
            if q < t1:
                vect = self.profile * hanning(
                    self.frequency, q * self.pulse_length, self.cycle
                )
            else:
                # src = - self.grid.E[self.x, self.y, self.z, 2]
                vect = self.profile * 0
        elif self.pulse_type == "gaussian":
            vect = self.profile * pulse_oscillation(frequency=self.frequency, t=q * self.grid.time_step,
                                                    pulselength=self.pulse_length, offset=self.offset)
        # if not pulse_type
        else:
            vect = self.profile * sin(2 * pi * q / self.period + self.phase_shift)
            # 要绘制光源图像只需绘制vect
        # do not use list indexing here, as this is much slower especially for torch backend
        # DISABLED: self.grid.E[self.x, self.y, self.z, 2] = vect
        self._Epol = 'xyz'.index(self.polarization)
        for x, y, z, value in zip(self.x, self.y, self.z, vect):
            # str.index(a)方法给出str中a的所在位置
            # self.grid.E[x, y, z, 0] += 3.7494e-33 * value
            self.grid.E[x, y, z, self._Epol] += value
            # self.grid.source_profile[self._Epol] += value
            # self.grid.E[x, y, z, 2] += value

    def update_H(self):
        """Add the source to the magnetic field"""

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(period={self.period}, "
            f"amplitude={self.amplitude}, phase_shift={self.phase_shift}, "
            f"name={repr(self.name)})"
        )

    def __str__(self):
        s = "    " + repr(self) + "\n"
        x = f"[{self.x[0]}, ... , {self.x[-1]}]"
        y = f"[{self.y[0]}, ... , {self.y[-1]}]"
        z = f"[{self.z[0]}, ... , {self.z[-1]}]"
        s += f"        @ x={x}, y={y}, z={z}\n"
        return s


## PlaneSource class
class PlaneSource:
    """A source along a plane in the FDTD grid"""

    def __init__(
            self,
            period: Number = 15,
            amplitude: float = 1.0,
            phase_shift: float = 0.0,
            waveform: str = "gaussian",
            name: str = None,
            polarization: str = 'z',
            pulse_type: str = None,
            pulse_length: float = 39e-15,
            offset: float = 112e-15,
            real_EH_unit: bool = True,
            axis: str = "y"
    ):
        """Create a PlaneSource.

        Args:
            period: The period of the source. The period can be specified
                as integer [timesteps] or as float [seconds]
            amplitude: The amplitude of the source in simulation units
            phase_shift: The phase offset of the source.
            waveform: "plane"代表平面波，“gaussian”代表高斯波形
            pulse_type: "gaussian"代表高斯脉冲 "hanning"代表汉宁脉冲 "none"或者其他任何输入代表不使用脉冲
            pulse_length: 脉宽(对于高斯脉冲：半高全宽*sqrt(2))单位s
            offset: 脉冲中心时间 修改于23.5.14 单位s
            cycle: cycles for Hanning window pulse.
            polarization: Axis of E-field polarization ('x','y',or 'z')电场偏振方向 "x" "y" "z"
            # TODO: 面光源的脉冲应该是怎样的？
        """
        self.grid = None
        self.period = period
        self.amplitude = amplitude
        if real_EH_unit:
            self.sim_amplitude = worldE_to_simE(amplitude)
        else:
            self.sim_amplitude = amplitude
        self.phase_shift = phase_shift
        self.waveform = waveform
        self.name = name
        self.polarization = polarization
        if pulse_type != "gaussian" and pulse_type != "hanning":
            self.pulse_type = None
        else:
            self.pulse_type = pulse_type
        self.frequency = 1.0 / period
        self.pulse_length = pulse_length
        self.offset = offset
        self.axis = axis

    def _register_grid(
            self, grid: Grid, x: ListOrSlice, y: ListOrSlice, z: ListOrSlice
    ):
        """Register a grid for the source.

        Args:
            grid: the grid to place the source into.
            x: The x-location of the source in the grid
            y: The y-location of the source in the grid
            z: The z-location of the source in the grid

        Note:
        As its name suggests, this source is a LINE source.
            Hence the source spans the diagonal of the cube
            defined by the slices in the grid.
        """
        self.grid = grid
        self.grid.sources.append(self)
        if self.name is not None:
            if not hasattr(grid, self.name):
                setattr(grid, self.name, self)
            else:
                raise ValueError(
                    f"The grid already has an attribute with name {self.name}"
                )

        self.x, self.y, self.z = self._handle_slices(x, y, z)

        self.period = grid._handle_time(self.period)

        x = bd.arange(self.x.start, self.x.stop, 1) - (self.x.start + self.x.stop) // 2
        y = bd.arange(self.y.start, self.y.stop, 1) - (self.y.start + self.y.stop) // 2
        z = bd.arange(self.z.start, self.z.stop, 1) - (self.z.start + self.z.stop) // 2
        xvec, yvec, zvec = bd.broadcast_arrays(
            x[:, None, None], y[None, :, None], z[None, None, :]
        )
        _xvec = bd.array(xvec, float)
        _yvec = bd.array(yvec, float)
        _zvec = bd.array(zvec, float)
        if self.waveform == "gaussian":
            sigma_x = max(0.5 * _xvec.max(), 1e-6)  # 避免除零
            sigma_y = max(0.5 * _yvec.max(), 1e-6)
            sigma_z = max(0.5 * _zvec.max(), 1e-6)
            profile = bd.exp(-(_xvec ** 2 / (2 * sigma_x ** 2) + _yvec ** 2 / (2 * sigma_y ** 2) + _zvec ** 2 / (2 * sigma_z ** 2)))
        else:
            profile = bd.ones(_xvec.shape)
        self.profile = self.sim_amplitude * profile

    def _handle_slices(
            self, x: ListOrSlice, y: ListOrSlice, z: ListOrSlice
    ) -> Tuple[List, List, List]:
        """Validate slices and calculate center of plane

        Args:
            x: The x-location of the volume in the grid
            y: The y-location of the volume in the grid
            z: The z-location of the volume in the grid

        Returns:
            x, y, z: the x, y and z coordinates of the source as slices

        """
        # ensure all slices
        if not isinstance(x, slice):
            if isinstance(x, list):
                (x,) = x
            x = slice(
                self.grid._handle_distance(x, "x"), self.grid._handle_distance(x, "x") + 1, None
            )
        if not isinstance(y, slice):
            if isinstance(y, list):
                (y,) = y
            y = slice(
                self.grid._handle_distance(y, "y"), self.grid._handle_distance(y, "y") + 1, None
            )
        if not isinstance(z, slice):
            if isinstance(z, list):
                (z,) = z
            z = slice(
                self.grid._handle_distance(z, "z"), self.grid._handle_distance(z, "z") + 1, None
            )

        # if we get here, we can assume slices:
        x0 = self.grid._handle_distance(x.start if x.start is not None else 0, "x")
        y0 = self.grid._handle_distance(y.start if y.start is not None else 0, "y")
        z0 = self.grid._handle_distance(z.start if z.start is not None else 0, "z")
        x1 = self.grid._handle_distance(x.stop if x.stop is not None else self.grid.Nx, "x")
        y1 = self.grid._handle_distance(y.stop if y.stop is not None else self.grid.Ny, "y")
        z1 = self.grid._handle_distance(z.stop if z.stop is not None else self.grid.Nz, "z")

        # make sure all slices have a start, stop and no step:
        x = (
            slice(x0, x1)
            if x0 < x1
            else (slice(x1, x0) if x0 > x1 else slice(x0, x0 + 1))
        )
        y = (
            slice(y0, y1)
            if y0 < y1
            else (slice(y1, y0) if y0 > y1 else slice(y0, y0 + 1))
        )
        z = (
            slice(z0, z1)
            if z0 < z1
            else (slice(z1, z0) if z0 > z1 else slice(z0, z0 + 1))
        )

        if [x.stop - x.start, y.stop - y.start, z.stop - z.start].count(0) > 0:
            raise ValueError(
                "Given location for PlaneSource results in slices of length 0!"
            )
        if [x.stop - x.start, y.stop - y.start, z.stop - z.start].count(1) == 0:
            raise ValueError("Given location for PlaneSource is not a 2D plane!")
        if [x.stop - x.start, y.stop - y.start, z.stop - z.start].count(1) > 1:
            raise ValueError(
                "Given location for PlaneSource should have no more than one dimension in which it's flat.\n"
                "Use a LineSource for lower dimensional sources."
            )

        self._Epol = 'xyz'.index(self.polarization)
        # str.index(a)方法给出str中a的所在位置
        if (x.stop - x.start == 1 and self.polarization == 'x') or \
                (y.stop - y.start == 1 and self.polarization == 'y') or \
                (z.stop - z.start == 1 and self.polarization == 'z'):
            raise ValueError(
                "PlaneSource cannot be polarized perpendicular to the orientation of the plane."
            )
        _Hpols = [(z, 1, 2), (z, 0, 2), (y, 0, 1)][self._Epol]
        if _Hpols[0].stop - _Hpols[0].start == 1:
            self._Hpol = _Hpols[1]
        else:
            self._Hpol = _Hpols[2]

        return x, y, z

    # def update_E(self):
    #     """Add the source to the electric field"""
    #     q = self.grid.time_steps_passed
    #     vect = self.profile * sin(2 * pi * q / self.period + self.phase_shift)
    #     self.grid.E[self.x, self.y, self.z, self._Epol] = vect

    def update_E(self):
        """Add the source to the electric field"""
        q = self.grid.time_steps_passed
        # if pulse is "hanning"
        if self.pulse_type == "hanning":
            t1 = int(2 * pi / (self.frequency * self.pulse_length / self.cycle))
            if q < t1:
                vect = self.profile * hanning(
                    self.frequency, q * self.pulse_length, self.cycle
                )
            else:
                # src = - self.grid.E[self.x, self.y, self.z, 2]
                vect = self.profile * 0
        elif self.pulse_type == "gaussian":
            vect = self.profile * pulse_oscillation(frequency=self.frequency, t=q * self.grid.time_step,
                                                    pulselength=self.pulse_length, offset=self.offset)
        # if not pulse_type
        else:
            vect = self.profile * sin(2 * pi * q / self.period + self.phase_shift)
            # 要绘制光源图像只需绘制vect
        # do not use list indexing here, as this is much slower especially for torch backend
        # DISABLED: self.grid.E[self.x, self.y, self.z, 2] = vect
        self._Epol = 'xyz'.index(self.polarization)
        # 与点光源和线光源（软源 soft source）不同，这应该是一个硬源 （hard source）
        self.grid.E[self.x, self.y, self.z, self._Epol] = vect

    def update_H(self):
        """Add the source to the magnetic field"""
        q = self.grid.time_steps_passed
        vect = self.profile * sin(2 * pi * q / self.period + self.phase_shift)
        self.grid.H[self.x, self.y, self.z, self._Hpol] = vect

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(period={self.period}, "
            f"amplitude={self.amplitude}, phase_shift={self.phase_shift}, "
            f"name={repr(self.name)}, polarization={repr(self.polarization)})"
        )

    def __str__(self):
        s = "    " + repr(self) + "\n"
        x = f"[{self.x.start}, ... , {self.x.stop}]"
        y = f"[{self.y.start}, ... , {self.y.stop}]"
        z = f"[{self.z.start}, ... , {self.z.stop}]"
        s += f"        @ x={x}, y={y}, z={z}\n"
        return s

    @property
    def bandwidth(self):
        if self.pulse_type is not None:
            return bandwidth(self.pulse_length)
        else:
            return 25e12


class SoftArbitraryPointSource:
    r"""

    A source placed at a single point (grid cell) in the grid.
    This source is special: it's both a source and a detector.

    Unlike the other sources, the input is a voltage, not an electric field.
    (really? why? should we convert back and forth?)

    For electrical measurements I've only needed a single-index source,
    so I don't know how the volume/line sources above work.
    We want the FFT function to operate over any detector.
    Maybe all sources should take an arbitary waveform argument?

    Each index in the *waveform* array represents 1 value at a timestep.

    There are many different *geometries* of "equivalent sources".
    The detector/source paradigm used in /fdtd might perhaps not correspond to this in an ideal
    fashion.

    It's not intuitively clear to me what a "soft" source would imply in the optical case, or what
    impedance even means for a laser.

    /fdtd/ seems to have found primary use in optical circles,
    so the default Z should probably be 0.

    "Whilst established for microwaves and electrical circuits,
    this concept has only very recently been observed in the optical domain,
    yet is not well defined or understood."[1]

    [1]: Optical impedance of metallic nano-structures, M. Mazilu and K. Dholakia
    https://doi.org/10.1364/OE.14.007709

    [2]: http://www.gwoptics.org/learn/02_Plane_waves/01_Fabry_Perot_cavity/02_Impedance_matched.php

    /\/\-
    """

    def __init__(
            self, waveform_array: ndarray, name: str = None, impedance: float = 0.0
    ):
        """Create



        Args:
            waveform_array
        """
        self.grid = None
        self.name = name
        self.current_detector = None
        self.waveform_array = waveform_array
        self.impedance = impedance
        self.input_voltage = []  # voltage hard-imposed by the source
        self.source_voltage = []  #
        # "field" rather than "voltage" might be more meaningful
        # FIXME: these voltage time histories have a different dimensionality

    def _register_grid(self, grid: Grid, x: Number, y: Number, z: Number):
        """Register a grid for the source.

        Args:
            grid: the grid to place the source into.
            x: The x-location of the source in the grid
            y: The y-location of the source in the grid
            z: The z-location of the source in the grid

        Note:
            As its name suggests, this source is a POINT source.
            Hence it should be placed at a single coordinate tuple
            int the grid.
        """
        self.grid = grid
        self.grid.sources.append(self)
        if self.name is not None:
            if not hasattr(grid, self.name):
                setattr(grid, self.name, self)
            else:
                raise ValueError(
                    f"The grid already has an attribute with name {self.name}"
                )

        try:
            (x,), (y,), (z,) = x, y, z
        except (TypeError, ValueError):
            raise ValueError("a point source should be placed on a single grid cell.")
        self.x, self.y, self.z = grid._handle_tuple((x, y, z))

        if self.name is not None:
            detector_name += "_I"
        else:
            detector_name = None

        self.current_detector = CurrentDetector(name=detector_name)
        grid[x, y, z] = self.current_detector

    def update_E(self):

        # It is important that this step happen between the E-field update and the
        # H-field update.

        if self.grid.time_steps_passed < self.waveform_array.shape[0]:
            # check for off-by-one error here
            input_voltage = self.waveform_array[self.grid.time_steps_passed]
        else:
            input_voltage = 0.0  # one could taper the last value off smoothly instead

        if self.grid.time_steps_passed > 0:
            current = self.current_detector.I[-1][0][0][0]
        else:
            current = 0.0

        if self.impedance > 0:
            source_resistive_voltage = self.impedance * current
            output_voltage = input_voltage + source_resistive_voltage
        else:
            output_voltage = input_voltage

        # right now, this does not compensate for the cell's permittivity!

        self.grid.E[self.x, self.y, self.z, 2] += (
                output_voltage / self.grid.grid_spacing
        )

        self.input_voltage.append([[[input_voltage]]])
        self.source_voltage.append([[[output_voltage]]])

    def update_H(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        s = "    " + repr(self) + "\n"
        x = f"{self.x}"
        y = f"{self.y}"
        z = f"{self.z}"
        s += f"        @ x={x}, y={y}, z={z}\n"
        return s
