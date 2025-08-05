""" visualization methods for the fdtd Grid.

This module supplies visualization methods for the FDTD Grid. They are
imported by the Grid class and hence are available as Grid methods.

"""

## Imports
import os

# plotting
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
from matplotlib.colors import LogNorm

# 3rd party
from tqdm import tqdm
from numpy import log10, where, sqrt, transpose, round
from scipy.signal import hilbert  # TODO: Write hilbert function to replace using scipy

# relative
from .backend import backend as bd
# from .backend import TorchCudaBackend
from . import conversions
from .fourier import FrequencyRoutines
from .detectors import *

from . import constants
import numpy as np

# 2D visualization function


def plot_structure(
        grid,
        x=None,
        y=None,
        z=None,
        cmap="Blues",
        pbcolor="C3",
        pmlcolor=(0, 0, 0, 0.1),
        objcolor=(1, 0, 0, 0.1),
        srccolor="C0",
        detcolor="C2",
        norm="linear",
        show=False,  # default False to allow animate to be true
        animate=False,  # True to see frame by frame states of grid while running simulation
        index=None,  # index for each frame of animation (visualize fn runs in a loop, loop variable is passed as index)
        save=False,  # True to save frames (requires parameters index, folder)
        folder=None,  # folder path to save frames
        geo: list = None,
        background_index: float = 1.0,
        show_structure: bool = True,
        show_energy: bool = False,
):
    """visualize a projection of the grid and the optical energy inside the grid

    Args:
        grid: photfdtd.fdtd.grid
        x: the x-value to make the yz-projection (leave None if using different projection)
        y: the y-value to make the zx-projection (leave None if using different projection)
        z: the z-value to make the xy-projection (leave None if using different projection)
        cmap: the colormap to visualize the energy in the grid
        pbcolor: the color to visualize the periodic boundaries
        pmlcolor: the color to visualize the PML
        objcolor: the color to visualize the objects in the grid
        srccolor: the color to visualize the sources in the grid
        detcolor: the color to visualize the detectors in the grid
        norm: how to normalize the grid_energy color map ('linear' or 'log').
        show: call pyplot.show() at the end of the function
        animate: see frame by frame state of grid during simulation
        index: index for each frame of animation (typically a loop variable is passed)
        save: save frames in a folder
        folder: path to folder to save frames
        @param background_index: 背景折射率
        @param geo:solve.geometry。若为None，程序会自动计算
    Note:
        grid should be a photfdtd.fdtd.Grid object, not photfdtd.Grid object.
    """
    if norm not in ("linear", "lin", "log"):
        raise ValueError("Color map normalization should be 'linear' or 'log'.")
    # imports (placed here to circumvent circular imports)
    from .sources import PointSource, LineSource, PlaneSource
    from .boundaries import _PeriodicBoundaryX, _PeriodicBoundaryY, _PeriodicBoundaryZ
    from .boundaries import (
        _PMLXlow,
        _PMLXhigh,
        _PMLYlow,
        _PMLYhigh,
        _PMLZlow,
        _PMLZhigh,
    )

    if animate:  # pause for 0.1s, clear plot
        plt.pause(0.02)
        plt.clf()
        plt.ion()  # ionteration on for animation effect

    # validate x, y and z
    if x is not None:
        if not isinstance(x, int):
            raise ValueError("the `x`-location supplied should be a single integer")
        if y is not None or z is not None:
            raise ValueError(
                "if an `x`-location is supplied, one should not supply a `y` or a `z`-location!"
            )
    elif y is not None:
        if not isinstance(y, int):
            raise ValueError("the `y`-location supplied should be a single integer")
        if z is not None or x is not None:
            raise ValueError(
                "if a `y`-location is supplied, one should not supply a `z` or a `x`-location!"
            )
    elif z is not None:
        if not isinstance(z, int):
            raise ValueError("the `z`-location supplied should be a single integer")
        if x is not None or y is not None:
            raise ValueError(
                "if a `z`-location is supplied, one should not supply a `x` or a `y`-location!"
            )
    else:
        raise ValueError(
            "at least one projection plane (x, y or z) should be supplied to visualize the grid!"
        )

    # just to create the right legend entries:
    legend = False
    if legend:
        plt.plot([], lw=7, color=objcolor, label="Objects")
        plt.plot([], lw=7, color=pmlcolor, label="PML")
        plt.plot([], lw=3, color=pbcolor, label="Periodic Boundaries")
        plt.plot([], lw=3, color=srccolor, label="Sources")
        plt.plot([], lw=3, color=detcolor, label="Detectors")

    # Grid energy
    if not show_energy:
        grid_energy = bd.zeros_like(grid.E[:,:,:,-1])
    else:
        grid_energy = bd.sum(grid.E ** 2 + grid.H ** 2, -1)
    if x is not None:
        assert grid.Ny > 1 and grid.Nz > 1
        xlabel, ylabel = "y/um", "z/um"
        Nx, Ny = grid.Ny, grid.Nz
        pbx, pby = _PeriodicBoundaryY, _PeriodicBoundaryZ
        pmlxl, pmlxh, pmlyl, pmlyh = _PMLYlow, _PMLYhigh, _PMLZlow, _PMLZhigh
        grid_energy = grid_energy[x, :, :].T
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ylim(-1, Ny)
        # plt.xlim(-1, Nx)
    elif y is not None:
        assert grid.Nx > 1 and grid.Nz > 1
        xlabel, ylabel = "x/um", "z/um"
        Nx, Ny = grid.Nx, grid.Nz
        pbx, pby = _PeriodicBoundaryX, _PeriodicBoundaryZ
        pmlxl, pmlxh, pmlyl, pmlyh = _PMLXlow, _PMLXhigh, _PMLZlow, _PMLZhigh
        grid_energy = grid_energy[:, y, :].T
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.gca().yaxis.set_ticks_position('left')
        plt.ylim(-1, Ny)
    elif z is not None:
        assert grid.Nx > 1 and grid.Ny > 1
        xlabel, ylabel = "x/um", "y/um"
        Nx, Ny = grid.Nx, grid.Ny
        pbx, pby = _PeriodicBoundaryX, _PeriodicBoundaryY
        pmlxl, pmlxh, pmlyl, pmlyh = _PMLXlow, _PMLXhigh, _PMLYlow, _PMLYhigh
        grid_energy = grid_energy[:, :, z].T
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ylim(-1, Ny)
    else:
        raise ValueError("Visualization only works for 2D grids")

    for source in grid.sources:
        if isinstance(source, LineSource):
            if x is not None:
                _x = [source.y[0], source.y[-1]]
                _y = [source.z[0], source.z[-1]]
            elif y is not None:
                _x = [source.x[0], source.x[-1]]
                _y = [source.z[0], source.z[-1]]
            elif z is not None:
                _x = [source.x[0], source.x[-1]]
                _y = [source.y[0], source.y[-1]]
            plt.plot(_x, _y, lw=3, color=srccolor)
        elif isinstance(source, PointSource):
            if x is not None:
                _x = source.y
                _y = source.z
            elif y is not None:
                _x = source.x
                _y = source.z
            elif z is not None:
                _x = source.x
                _y = source.y
            plt.plot(_x - 0.5, _y - 0.5, lw=3, marker="o", color=srccolor)
            # 由于grid_energy在前面被转置，这里必须对_x与_y做替换
            grid_energy[_y, _x] = 0  # do not visualize energy at location of source
        elif isinstance(source, PlaneSource):
            if x is not None:
                _x = (
                    source.y
                    if source.y.stop > source.y.start + 1
                    else slice(source.y.start, source.y.start)
                )
                _y = (
                    source.z
                    if source.z.stop > source.z.start + 1
                    else slice(source.z.start, source.z.start)
                )
            elif y is not None:
                _x = (
                    source.x
                    if source.x.stop > source.x.start + 1
                    else slice(source.x.start, source.x.start)
                )
                _y = (
                    source.z
                    if source.z.stop > source.z.start + 1
                    else slice(source.z.start, source.z.start)
                )
            elif z is not None:
                _x = (
                    source.x
                    if source.x.stop > source.x.start + 1
                    else slice(source.x.start, source.x.start)
                )
                _y = (
                    source.y
                    if source.y.stop > source.y.start + 1
                    else slice(source.y.start, source.y.start)
                )

            patch = ptc.Rectangle(
                xy=(_x.start - 0.5, _y.start - 0.5),
                width=_x.stop - _x.start,
                height=_y.stop - _y.start,
                linewidth=0,
                edgecolor=srccolor,
                facecolor=srccolor,
            )
            plt.gca().add_patch(patch)

    # Detector
    for detector in grid.detectors:
        if x is not None:
            _x = [detector.y[0], detector.y[-1]]
            _y = [detector.z[0], detector.z[-1]]
        elif y is not None:
            _x = [detector.x[0], detector.x[-1]]
            _y = [detector.z[0], detector.z[-1]]
        elif z is not None:
            _x = [detector.x[0], detector.x[-1]]
            _y = [detector.y[0], detector.y[-1]]

        if detector.__class__.__name__ == "BlockDetector":
            # BlockDetector
            plt.plot(
                [_x[0], _x[1], _x[1], _x[0], _x[0]],
                [_y[0], _y[0], _y[1], _y[1], _y[0]],
                lw=3,
                color=detcolor,
            )
        else:
            # LineDetector
            plt.plot(_x, _y, lw=3, color=detcolor)

    # Boundaries
    for boundary in grid.boundaries:
        # TODO: 日后使用周期边界时要注意绘图问题
        if isinstance(boundary, pbx):
            _x = [-0.5, -0.5, float("nan"), Nx - 0.5, Nx - 0.5]
            _y = [-0.5, Ny - 0.5, float("nan"), -0.5, Ny - 0.5]
            # *
            plt.plot(_y, _x, color=pbcolor, linewidth=3)
        elif isinstance(boundary, pby):
            _x = [-0.5, Nx - 0.5, float("nan"), -0.5, Nx - 0.5]
            _y = [-0.5, -0.5, float("nan"), Ny - 0.5, Ny - 0.5]
            # *
            plt.plot(_y, _x, color=pbcolor, linewidth=3)
        elif isinstance(boundary, pmlyl):
            patch = ptc.Rectangle(
                xy=(-0.5, -0.5),
                width=Nx,
                height=boundary.thickness,
                linewidth=0,
                edgecolor="none",
                facecolor=pmlcolor,
            )
            plt.gca().add_patch(patch)
        elif isinstance(boundary, pmlxl):
            patch = ptc.Rectangle(
                xy=(-0.5, -0.5),
                width=boundary.thickness,
                height=Ny,
                linewidth=0,
                edgecolor="none",
                facecolor=pmlcolor,
            )
            plt.gca().add_patch(patch)
        elif isinstance(boundary, pmlyh):
            patch = ptc.Rectangle(
                xy=(-0.5, Ny + 0.5 - boundary.thickness),
                width=Nx,
                height=boundary.thickness,
                linewidth=0,
                edgecolor="none",
                facecolor=pmlcolor,
            )
            plt.gca().add_patch(patch)
        elif isinstance(boundary, pmlxh):
            patch = ptc.Rectangle(
                xy=(Nx - boundary.thickness + 0.5, -0.5),
                width=boundary.thickness,
                height=Ny,
                linewidth=0,
                edgecolor="none",
                facecolor=pmlcolor,
            )
            plt.gca().add_patch(patch)
    # 只显示波导结构的轮廓，而不显示整个波导
    if show_structure:
        if geo is None:
            # if bd.__class__ == TorchCudaBackend:
            inv_eps = bd.numpy(grid.inverse_permittivity)
            # else:
            #     inv_eps = grid.inverse_permittivity
            geo = bd.sqrt(1 / inv_eps)

        # geo是四维矩阵
        geo = geo[:, :, :, -1]
        if x is not None:
            n_to_draw = geo[x, :, :]
        elif y is not None:
            n_to_draw = geo[:, y, :]
        elif z is not None:
            n_to_draw = geo[:, :, z]
        # n_to_draw /= n_to_draw.max()
        contour_data = where(bd.numpy(n_to_draw) != bd.numpy(background_index), 1, 0)
        plt.contour(contour_data.T, colors='black', linewidths=1)

    # for obj in grid.objects:
    #     if x is not None:
    #         _x = (obj.y.start, obj.y.stop)
    #         _y = (obj.z.start, obj.z.stop)
    #     elif y is not None:
    #         _x = (obj.z.start, obj.z.stop)
    #         _y = (obj.x.start, obj.x.stop)
    #     elif z is not None:
    #         _x = (obj.x.start, obj.x.stop)
    #         _y = (obj.y.start, obj.y.stop)
    #
    #     patch = ptc.Rectangle(
    #         xy=(min(_y) - 0.5, min(_x) - 0.5),
    #         width=max(_y) - min(_y),
    #         height=max(_x) - min(_x),
    #         linewidth=0,
    #         edgecolor="none",
    #         facecolor=objcolor,
    #     )
    #     plt.gca().add_patch(patch)

    # visualize the energy in the grid
    cmap_norm = None
    if norm == "log":
        cmap_norm = LogNorm(vmin=1e-4, vmax=grid_energy.max() + 1e-4)
    plt.imshow(bd.numpy(grid_energy), cmap=cmap, interpolation="sinc", norm=cmap_norm)
    # 由于在前面对grid_energy做了转置，所以grid_energy.shape[0]实际上是竖直方向而grid_energy.shape[1]是水平方向
    if grid_energy.shape[1] * grid.grid_spacing < 10e-6:
        xticks = bd.arange(0, grid_energy.shape[1], int((1e-6) / grid.grid_spacing))
    else:
        xticks = bd.arange(0, grid_energy.shape[1], int((10e-6) / grid.grid_spacing))
        
    if grid_energy.shape[0] * grid.grid_spacing < 10e-6:
        yticks = bd.arange(0, grid_energy.shape[0], int((1e-6) / grid.grid_spacing))
    else:
        yticks = bd.arange(0, grid_energy.shape[0], int((10e-6) / grid.grid_spacing))

    xlabels = xticks * grid.grid_spacing * 1e6
    ylabels = yticks * grid.grid_spacing * 1e6
    xlabels = bd.numpy(round(xlabels)).astype(int).tolist()
    ylabels = bd.numpy(round(ylabels)).astype(int).tolist()

    #
    plt.xticks(xticks, xlabels)
    plt.yticks(yticks, ylabels)
    # # finalize the plot
    # plt.ylabel(xlabel)
    # plt.xlabel(ylabel)
    # plt.ylim(Nx, -1)
    # plt.xlim(-1, Ny)
    # plt.figlegend()
    plt.tight_layout()
    # plt.axis("tight")
    # save frame (require folder path and index)
    if save:
        plt.savefig(os.path.join(folder, f"file{str(index).zfill(4)}.png"))

    # show if not animating
    if show:
        plt.show()
        
def save_fig(grid,
             axis=None,
             axis_index=None,
             axis_number=None,
             animate=False,
             geo=None,
             show_structure=True,
             show_energy=False):
    """
    Saving the geometry figure. This function can also show energy while show_energy = True.
    @param geo: Refractive index profile, will be calculated automatically if None. 也可以为None，程序会自己计算
    @param axis: axis to plot. 轴(若为二维XY模拟，则axis只能='z')
    @param axis_index: index of axis
    @param axis_number: an outdated version of axis_index
    @param animate: 是否生成动画。
    @param show_structure: 是否显示结构
    @param show_energy: 是否显示能量分布
    @return: None
    """
    if not axis:
        # Tell which dimension to draw automatically
        dims_with_size_one = [i for i, size in enumerate(grid._grid.inverse_permittivity.shape) if size == 1]
        if not dims_with_size_one:
            axis = "y"
        else:
            axis = conversions.number_to_letter(dims_with_size_one[0])

    if axis_index is None:
        if axis_number is None:
            axis_index = int(grid._grid.Ny / 2)
        else:
            axis_index = axis_number

    if not show_energy:
        time = 0

    else:
        time = grid._grid.time_steps_passed
    index = "_%s=%d, total_time=%d" % (axis, axis_index, time)
    if grid._grid is None:
        raise RuntimeError("The grid should have been set before saving figure.")

    axis = axis.lower()  # 识别大写的 "X"
    folder = grid.folder
    if axis == "x":  # 绘制截面/剖面场图
        plot_structure(grid=grid._grid, x=axis_index, save=True, animate=animate,
                                  index=index, folder=folder, geo=geo,
                                  background_index=grid.background_index, show_structure=show_structure,
                                  show_energy=show_energy)
    elif axis == "y":
        plot_structure(grid=grid._grid, y=axis_index, save=True, animate=animate,
                                  index=index, folder=folder, geo=geo,
                                  background_index=grid.background_index, show_structure=show_structure,
                                  show_energy=show_energy)
    elif axis == "z":
        plot_structure(grid=grid._grid, z=axis_index, save=True, animate=animate,
                                  index=index, folder=folder, geo=geo,
                                  background_index=grid.background_index, show_structure=show_structure,
                                  show_energy=show_energy)
    else:
        raise ValueError("Unknown axis parameter.")

    plt.close()  # 清除画布

def plot_n(grid,
           axis: str = None,
           axis_index: int = 0,
           filepath: str = None):
    """
    Draw a refractive index plot. It is basically same with solve.plot().
    @param axis: axis to plot, can be 'x', 'y' or 'z'. If None, it will be automatically determined.
    @param axis_index: index of axis, default to 0.
    @param filepath: the path to save the figure. If None, it will be saved in the folder of the grid.
    @return: None
    """
    if not axis:
        # Tell which dimension to draw automatically
        dims_with_size_one = [i for i, size in enumerate(grid._grid.inverse_permittivity.shape) if size == 1]
        if not dims_with_size_one:
            axis = "y"
            axis_index = int(grid._grid.Ny / 2)
        else:
            axis = conversions.number_to_letter(dims_with_size_one[0])

    if not filepath:
        filepath = grid.folder
    grid = grid._grid
    geometry = bd.sqrt(1 / bd.to_float(grid.inverse_permittivity))
    axis = axis.lower()

    # 去掉作为轴的那一维
    if axis == 'x':
        n = geometry[axis_index, :, :, :]
    elif axis == 'y':
        n = geometry[:, axis_index, :, :]
    elif axis == 'z':
        n = geometry[:, :, axis_index, :]
    else:
        raise ValueError('Parameter "axis" should be x, y or z! ')
    x = n.shape[0]
    y = n.shape[1]

    # It's quite important to transpose n
    from matplotlib import cm
    n = bd.transpose(n, [1, 0, 2])

    if axis == "x":
        plt.xlabel('y/um')
        plt.ylabel('z/um')
        x_stick = x * grid.grid_spacing_y * 1e6
        y_stick = y * grid.grid_spacing_z * 1e6
    elif axis == "y":
        plt.xlabel('x/um')
        plt.ylabel('z/um')
        x_stick = x * grid.grid_spacing_x * 1e6
        y_stick = y * grid.grid_spacing_z * 1e6
    elif axis == "z":
        plt.xlabel('x/um')
        plt.ylabel('y/um')
        x_stick = x * grid.grid_spacing_x * 1e6
        y_stick = y * grid.grid_spacing_y * 1e6
    plt.imshow(bd.numpy(n[:, :, 0]), cmap=cm.jet, origin="lower",
               extent=[0, x_stick, 0, y_stick])
    plt.clim([bd.min(n), bd.max(n)])
    plt.colorbar()
    plt.title("refractive_index_real")
    # 保存图片
    plt.savefig(fname='%s\\%s_%s=%d.png' % (filepath, 'index', axis, axis_index))

    # plt.show()
    plt.clf()
    plt.close()


def dB_map_2D(block_det=None, interpolation="spline16", axis="z", field="E", field_axis="z", save=True,
              folder="", name_det="", total_time=0):
    """
    Displays detector readings from an 'fdtd.BlockDetector' in a decibel map spanning a 2D slice region inside the BlockDetector.
    Compatible with continuous sources (not waveform).

    Parameter:-
        block_det (numpy array): 5 axes numpy array (timestep, row, column, height, {x, y, z} parameter) created by 'fdtd.BlockDetector'.
        (optional) interpolation (string): Preferred 'matplotlib.pyplot.imshow' interpolation. Default "spline16".
        @param axis: 选择截面"x" or "y" or "z"
        @param save: 是否保存
        @param folder: 存储文件夹
        @param name_det: 面监视器的名称
        @param total_time: 总模拟时间，可选，仅为了命名
    """
    # if block_det is None:
    #     raise ValueError(
    #         "Function 'dBmap' requires a detector_readings object as parameter."
    #     )
    # if len(block_det.shape) != 5:  # BlockDetector readings object have 5 axes
    #     raise ValueError(
    #         "Function 'dBmap' requires object of readings recorded by 'fdtd.BlockDetector'."
    #     )

    # TODO: convert all 2D slices (y-z, x-z plots) into x-y plot data structure
    plt.ioff()
    plt.close()
    a = []  # array to store wave intensities
    # 首先计算仿真空间上每一点在所有时间上的最大值与最小值之差

    if not axis:
        # Tell which dimension to draw automatically
        shape = block_det.shape
        dims_with_size_one = [i for i, size in enumerate(shape[1:], start=1) if size == 1]
        axis_number = dims_with_size_one[0]
        axis = conversions.number_to_letter(axis_number)

    choose_axis = conversions.letter_to_number(field_axis)

    if axis == "z":
        for i in tqdm(range(len(block_det[0]))):
            a.append([])
            for j in range(len(block_det[0][0])):
                temp = [x[i][j][0][choose_axis] for x in block_det]
                a[i].append(max(temp) - min(temp))
    elif axis == "x":
        for i in tqdm(range(len(block_det[0][0]))):
            a.append([])
            for j in range(len(block_det[0][0][0])):
                temp = [x[0][i][j][choose_axis] for x in block_det]
                a[i].append(max(temp) - min(temp))
    elif axis == "y":
        for i in tqdm(range(len(block_det[0]))):
            a.append([])
            for j in range(len(block_det[0][0][0])):
                temp = [x[i][0][j][choose_axis] for x in block_det]
                a[i].append(max(temp) - min(temp))

    peakVal, minVal = max(map(max, a)), min(map(min, a))
    # print(
    #     "Peak at:",
    #     [
    #         [[i, j] for j, y in enumerate(x) if y == peakVal]
    #         for i, x in enumerate(a)
    #         if peakVal in x
    #     ],
    # )
    # 然后做对数计算
    if minVal == 0:
        raise RuntimeError("minVal == 0, impossible to draw a dB map")
    a = 10 * log10([[y / minVal for y in x] for x in a])

    # plt.title("dB map of Electrical waves in detector region")
    plt.imshow(transpose(a), cmap="inferno", interpolation=interpolation)
    plt.ylim(-1, a.shape[1])
    if axis == "z":
        plt.xlabel('X/grids')
        plt.ylabel('Y/grids')
    elif axis == "x":
        plt.xlabel('Y/grids')
        plt.ylabel('Z/grids')
    elif axis == "y":
        plt.xlabel('X/grids')
        plt.ylabel('Z/grids')
    cbar = plt.colorbar()
    # cbar.ax.set_ylabel("dB scale", rotation=270)
    # plt.show()
    if save:
        fieldaxis = field + field_axis
        plt.savefig(fname='%s//dB_map_%s, detector_name=%s, time=%i.png' % (folder, fieldaxis, name_det, total_time))
    plt.close()


def plot_detection(detector_dict=None, specific_plot=None):
    """
    #TODO: 这个函数以前从来没用过
    1. Plots intensity readings on array of 'fdtd.LineDetector' as a function of timestep.
    2. Plots time of arrival of waveform at different LineDetector in array.
    Compatible with waveform sources.

    Args:
        detector_dict (dictionary): Dictionary of detector readings, as created by 'fdtd.Grid.save_data()'.
        (optional) specific_plot (string): Plot for a specific axis data. Choose from {"Ex", "Ey", "Ez", "Hx", "Hy", "Hz"}.
    """
    if detector_dict is None:
        raise Exception(
            "Function plotDetection() requires a dictionary of detector readings as 'detector_dict' parameter."
        )
    detectorElement = 0  # cell to consider in each detectors
    maxArray = {}
    plt.ioff()
    plt.close()

    for detector in detector_dict:
        if len(detector_dict[detector].shape) != 3:
            print("Detector '{}' not LineDetector; dumped.".format(detector))
            continue
        if specific_plot is not None:
            if detector[-2] != specific_plot[0]:
                continue
        if detector[-2] == "E":
            plt.figure(0, figsize=(15, 15))
        elif detector[-2] == "H":
            plt.figure(1, figsize=(15, 15))
        for dimension in range(len(detector_dict[detector][0][0])):
            if specific_plot is not None:
                if ["x", "y", "z"].index(specific_plot[1]) != dimension:
                    continue
            # if specific_plot, subplot on 1x1, else subplot on 2x2
            plt.subplot(
                2 - int(specific_plot is not None),
                2 - int(specific_plot is not None),
                dimension + 1 if specific_plot is None else 1,
            )
            hilbertPlot = abs(
                hilbert([x[0][dimension] for x in detector_dict[detector]])
            )
            plt.plot(hilbertPlot, label=detector)
            plt.title(detector[-2] + "(" + ["x", "y", "z"][dimension] + ")")
            if detector[-2] not in maxArray:
                maxArray[detector[-2]] = {}
            if str(dimension) not in maxArray[detector[-2]]:
                maxArray[detector[-2]][str(dimension)] = []
            maxArray[detector[-2]][str(dimension)].append(
                [detector, where(hilbertPlot == max(hilbertPlot))[0][0]]
            )

    # Loop same as above, only to add axes labels
    for i in range(2):
        if specific_plot is not None:
            if ["E", "H"][i] != specific_plot[0]:
                continue
        plt.figure(i)
        for dimension in range(len(detector_dict[detector][0][0])):
            if specific_plot is not None:
                if ["x", "y", "z"].index(specific_plot[1]) != dimension:
                    continue
            plt.subplot(
                2 - int(specific_plot is not None),
                2 - int(specific_plot is not None),
                dimension + 1 if specific_plot is None else 1,
            )
            plt.xlabel("Time steps")
            plt.ylabel("Magnitude")
        plt.suptitle("Intensity profile")
    plt.legend()
    plt.show()

    for item in maxArray:
        plt.figure(figsize=(15, 15))
        for dimension in maxArray[item]:
            arrival = bd.numpy(maxArray[item][dimension])
            plt.plot(
                [int(x) for x in arrival.T[1]],
                arrival.T[0],
                label=["x", "y", "z"][int(dimension)],
            )
        plt.title(item)
        plt.xlabel("Time of arrival (time steps)")
        plt.legend()
        plt.suptitle("Time-of-arrival plot")
    plt.show()

def dB_map(grid=None, folder=None, axis=None, field="E", field_axis="z",
           interpolation="spline16", total_time=None, save: bool = True):
    """
    Draw a field dB_map. At least 1 block detector is required. 绘制场分贝图 需要面监视器数据
    @param grid: Photfdtd.Grid
    @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
    @param axis: "x" or "y" or "z" 选择绘制dB图的截面
    @param field_axis: {x,y,z} of "E" or "H" field
    @param field: “E”或“H”
    @param interpolation: Optional. 'matplotlib.pyplot.imshow' interpolation 绘图方式
    @param save: bool, to save or not. 是否保存
    @param total_time: Optional, only used for title 模拟经历的时间，可选，仅命名用


    """
    print("Drawing dB map is not available currently.")
    return
    # FIXME: 由于detector数据保存方式的修改，该函数目前无法使用。需要读取h5文件
    if not axis:
        # Tell which dimension to draw automatically
        dims_with_size_one = [i for i, size in enumerate(grid._grid.inverse_permittivity.shape) if size == 1]
        if not dims_with_size_one:
            raise ValueError("Parameter 'axis' should not be None for 3D simulation")
        axis = conversions.number_to_letter(dims_with_size_one[0])
    if not folder:
        folder = grid.folder
    if not total_time:
        total_time = grid._grid.time_passed
    for detector in grid._grid.detectors:
        if isinstance(detector, fdtd.detectors.BlockDetector):
            fdtd.dB_map_2D(block_det=bd.array([x for x in detector.detector_values()["%s" % field]]),
                           interpolation=interpolation, axis=axis, field=field, field_axis=field_axis,
                           save=save, folder=folder, name_det=detector.name, total_time=total_time)

        # dic[detector.name + " (E)"] = bd.array([x for x in detector.detector_values()["E"]])
        # dic[detector.name + " (H)"] = bd.array([x for x in detector.detector_values()["H"]])
    # if block_det != None:
    #     data = block_det
    #     name_det = block_det.name
    # else:
    #     data = data[name_det + " (%s)" % field]

def plot_field(grid=None, axis="y", axis_index=0, field="E", field_axis=None, folder=None, cmap="jet",
               show_geometry=True, show_field=True, vmax=None, vmin=None):
    """
    Plot a field map at current state. No need for detectors. 绘制当前时刻场分布（不需要监视器）
    @param show_geometry: bool 是否绘制波导结构
    @param show_field: bool 是否绘制场
    @param grid: Photfdtd.Grid
    @param field: "E"或"H"
    @param field_axis: {x,y,z,None} of E or H, if None, the energy intensity of E or H will be plotted
    @param axis: "x"或"y"或"z"表示绘制哪个截面
    @param axis_index: 例如绘制z=0截面 ，则axis设为"z"而axis_index为0
    @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
    @param cmap: Optional. matplotlib.pyplot.imshow(cmap)
    @param vmax: Optional. Max value of the color bar. 颜色条的最大、最小值
    @param vmin: Optional. Min value of the color bar.
    """

    if not show_field:
        title = "%s=%i" % (axis, axis_index)
    elif not field_axis:
        title = "%s^2" % field
    else:
        title = f"{field}{field_axis}"
    if not folder:
        folder = grid.folder
    background_index = grid.background_index
    grid = grid._grid
    if not show_field:
        if axis == "z":
            field = bd.zeros_like(grid.E[:, :, axis_index, 0])
        elif axis == "y":
            field = bd.zeros_like(grid.E[:, axis_index, :, 0])
        elif axis == "x":
            field = bd.zeros_like(grid.E[axis_index, :, :, 0])
    else:
        if field == "E":
            if not field_axis:
                # 能量
                # TODO：这种算能量的方法对吗
                if axis == "z":
                    field = grid.E[:, :, axis_index, 0] ** 2 + grid.E[:, :, axis_index, 1] ** 2 + grid.E[:, :,
                                                                                                  axis_index,
                                                                                                  2] ** 2
                elif axis == "y":
                    field = grid.E[:, axis_index, :, 0] ** 2 + grid.E[:, axis_index, :, 1] ** 2 + grid.E[:,
                                                                                                  axis_index,
                                                                                                  :, 2] ** 2
                elif axis == "x":
                    field = grid.E[axis_index, :, :, 0] ** 2 + grid.E[axis_index, :, :, 1] ** 2 + grid.E[axis_index,
                                                                                                  :,
                                                                                                  :, 2] ** 2
            else:
                if axis == "z":
                    field = grid.E[:, :, axis_index, ord(field_axis) - 120]
                elif axis == "y":
                    field = grid.E[:, axis_index, :, ord(field_axis) - 120]
                elif axis == "x":
                    field = grid.E[axis_index, :, :, ord(field_axis) - 120]
        elif field == "H":
            if not field_axis:
                # 能量
                if axis == "z":
                    field = grid.H[:, :, axis_index, 0] ** 2 + grid.H[:, :, axis_index, 1] ** 2 + grid.H[:, :,
                                                                                                  axis_index,
                                                                                                  2] ** 2
                elif axis == "y":
                    field = grid.H[:, axis_index, :, 0] ** 2 + grid.H[:, axis_index, :, 1] ** 2 + grid.H[:,
                                                                                                  axis_index,
                                                                                                  :, 2] ** 2
                elif axis == "x":
                    field = grid.H[axis_index, :, :, 0] ** 2 + grid.H[axis_index, :, :, 1] ** 2 + grid.H[axis_index,
                                                                                                  :,
                                                                                                  :, 2] ** 2
            else:
                if axis == "z":
                    field = grid.H[:, :, axis_index, ord(field_axis) - 120]
                elif axis == "y":
                    field = grid.H[:, axis_index, :, ord(field_axis) - 120]
                elif axis == "x":
                    field = grid.H[axis_index, :, :, ord(field_axis) - 120]
        if not vmax:
            # vmax = max(abs(field.min().item()), abs(field.max().item()))
            vmax = field.max().item()
        if not vmin:
            if not field_axis:
                vmin = 0
            else:
                vmin = field.min().item()

    # 创建颜色图
    plt.figure()
    if axis == "x":
        x_stick = field.shape[0] * grid.grid_spacing_y * 1e6
        y_stick = field.shape[1] * grid.grid_spacing_z * 1e6
    if axis == "y":
        x_stick = field.shape[0] * grid.grid_spacing_x * 1e6
        y_stick = field.shape[1] * grid.grid_spacing_z * 1e6
    if axis == "z":
        x_stick = field.shape[0] * grid.grid_spacing_x * 1e6
        y_stick = field.shape[1] * grid.grid_spacing_y * 1e6
    field = bd.numpy(field)
    plt.imshow(bd.transpose(field), vmin=vmin, vmax=vmax, cmap=cmap,
               extent=[0, x_stick, 0, y_stick],
               origin="lower")  # cmap 可以选择不同的颜色映射
    if show_field:
        cbar = plt.colorbar()
    if show_geometry:
        geo = bd.sqrt(1 / bd.to_float(grid.inverse_permittivity))

        # geo是四维矩阵，取最后一个维度
        geo = geo[:, :, :, -1]

        # 根据不同的轴选择截面
        if axis == "x":
            n_to_draw = geo[axis_index, :, :]
        elif axis == "y":
            n_to_draw = geo[:, axis_index, :]
        elif axis == "z":
            n_to_draw = geo[:, :, axis_index]

        # 创建轮廓数据
        contour_data = bd.where(n_to_draw != bd.array(background_index), 1, 0)

        plt.contour(
            bd.numpy(bd.linspace(0, x_stick, field.shape[0])),
            bd.numpy(bd.linspace(0, y_stick, field.shape[1])),
            bd.numpy(contour_data.T),
            colors='black', linewidths=1)

    # plt.ylim(-1, field.shape[1])
    # Make the figure full the canvas让画面铺满整个画布
    # plt.axis("tight")
    # 添加颜色条

    # cbar.set_label('')

    # 添加标题和坐标轴标签
    plt.title(f"{title}")

    if axis == "z":
        plt.xlabel('x/um')
        plt.ylabel('y/um')
    elif axis == "x":
        plt.xlabel('y/um')
        plt.ylabel('z/um')
    elif axis == "y":
        plt.xlabel('x/um')
        plt.ylabel('z/um')
    if show_field:
        fname = "%s//%s_%s=%i.png" % (folder, title, axis, axis_index)
    else:
        fname = "%s//%s.png" % (folder, title)
    plt.savefig(fname=fname)
    plt.close()

def plot_fieldtime(grid=None, folder=None, field_axis="z", field="E", index=None, index_3d=None, name_det=None):
    """
    Draw and save the field vs time of a point, no use currently. 绘制监视器某一点的时域场图 没什么用
    @param grid: Photfdtd.Grid
    @param folder: Optional. The folder path to save the dB map. Default to grid.folder. 保存图片的地址，默认为grid.folder
    @param data: read_simulation()读到的数据
    @param field_axis: x, y, z of E or H
    @param field: “E“或”H“
    @param index: 用于线监视器，选择读取数据的点
    @param index_3d: 三维数组：用于面监视器，选择读取数据的点
    @param name_det: 监视器的名称
    """
    return
    data = None
    for detector in grid._grid.detectors:
        if detector.name == name_det:
            if field == "E":
                data = bd.array(detector.real_E())
            elif field == "H":
                data = bd.array(detector.real_H())
            else:
                raise ValueError("Parameter field should be either 'E' or 'H")
    if data is None:
        print("ValueError when using plot_fieldtime: No detector named '%s'" % name_det)
        return
    if folder is None:
        folder = grid.folder
    plt.figure()

    if data.ndim == 3:
        if index == None:
            index = int(data.shape[1] / 2)
        plt.plot(range(len(data)), data[:, index, ord(field_axis) - 120], linestyle='-', label="Experiment")
        plt.ylabel('%s%s' % (field, field_axis))
        plt.xlabel("timesteps")
        plt.title("%s%s-t" % (field, field_axis))
        file_name = "%s%s" % (field, field_axis)
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()
    else:
        if index_3d == None:
            index_3d = [int(data.shape[0] / 2), int(data.shape[1] / 2), int(data.shape[2] / 2)]
        plt.plot(range(len(data)), data[:, index_3d[0], index_3d[1], index_3d[2], ord(field_axis) - 120],
                 linestyle='-',
                 label="Experiment")
        plt.ylabel('%s%s' % (field, field_axis))
        plt.xlabel("timesteps")
        plt.title("%s%s-t" % (field, field_axis))
        file_name = "%s%s" % (field, field_axis)
        plt.savefig(os.path.join(folder, f"{file_name}.png"))
        plt.close()

def visualize_single_detector(grid,
                              detector=None,
                              name_det=None,
                              index=0,
                              index_3d=None,
                              field_axis="x",
                              field="E"):
    """
    Visualization of the result of a single detector
    绘制单个监视器的结果
    @param detector: photfdtd.grid.detector
    @param name_det: 监视器名称
    @param index: 用于线监视器，选择读取数据的点
    @param index_3d: 用于面监视器，选择读取数据的点
    @param field_axis: "x", "y", "z"
    @param field: ”E"或"H"
    @return frequency, original spectrum (complex): 频率和频谱
    关于傅里叶变换后的单位：有的人说是原单位，有的人说是原单位乘以积分时积的单位(s)
    https://stackoverflow.com/questions/1523814/units-of-a-fourier-transform-fft-when-doing-spectral-analysis-of-a-signal
    """
    # TODO: 把fdtd的fourier.py研究明白
    if field_axis is not None:
        # 如果field_axis是字母，转换为数字
        if field_axis in ["x", "y", "z"]:
            field_axis = conversions.letter_to_number(field_axis)
    if detector is None and name_det is not None:
        # 通过监视器名称找到监视器
        for d in grid._grid.detectors:
            if d.name == name_det:
                detector = d

    if name_det is None:
        name_det = detector.name

    if field == "E":
        data = grid.read_detector(name_det=name_det)[0]
    elif field == "H":
        data = grid.read_detector(name_det=name_det)[1]
    # if field == "E":
    #     data = bd.array(detector.real_E())
    # elif field == "H":
    #     data = bd.array(detector.real_H())
    else:
        raise ValueError("Parameter field should be either 'E' or 'H")
    data = bd.numpy(data)
    # if data is None:
    #     detector = grid._grid.detectors[0]
    #     data = bd.array([x for x in detector.detector_values()["%s" % field]])

    shape = data.shape
    if data.ndim == 3:
        # 线监视器
        if not index:
            index = int(shape[1] / 2)
        indexed_data = data[:, index, field_axis]
    elif data.ndim == 5:
        # 面监视器
        if not index_3d:
            index_3d = [int(shape[1] / 2), int(shape[2] / 2), int(shape[3] / 2)]
        indexed_data = data[:, index_3d[0], index_3d[1], index_3d[2], field_axis]

    # Spectrum
    # TODO: consider multiple sources?考虑有不同光源的情况？
    source = grid._try_to_find_source()
    fr = FrequencyRoutines(grid._grid, objs=indexed_data)
    spectrum_freqs, spectrum = fr.FFT(
        freq_window_tuple=[source.frequency - source.bandwidth,
                           source.frequency + source.bandwidth], )
    # spectrum是复值

    ### 试试ufdtd书中的方法，对空间中每个点的电场分别傅里叶变换
    # F = bd.empty(shape=data[0].shape, dtype=object)
    # for i in range(data[0].shape[0]):
    #     for j in range(3):
    #         fr = FrequencyRoutines(grid._grid, objs=data[:, i, j])
    #         spectrum_freqs, spectrum = fr.FFT(
    #             freq_window_tuple=[source.frequency - source.bandwidth,
    #                             source.frequency + source.bandwidth], )
    #         F[i, j] = abs(spectrum)
    ###

    # TODO: 目前只考虑了线监视器
    length = bd.numpy(bd.linspace(0, shape[1], shape[1]) * grid._grid.grid_spacing_x)
    time = bd.numpy(bd.linspace(0, shape[0], shape[0]) * grid._grid.time_step * 1e15)

    # 创建一个画布，包含两个子图
    fig, axes = plt.subplots(2, 2, figsize=(12, 6))  # 1行2列的子图

    # 左侧子图: Space distribution at when the field is maximum
    flattened_index = np.argmax(data)
    time_step_max_field = np.unravel_index(flattened_index, data.shape)[0]
    if data.ndim == 3:
        axes[0][0].plot(length * 1e6, data[time_step_max_field, :, field_axis])
        # axes[0][0].set_xticks()  # 每隔10个显示一个刻度
        axes[0][0].set_xlabel('um')
        axes[0][0].set_ylabel("E (V/m)")
        axes[0][0].set_title(f"Space distribution of {name_det} at {time_step_max_field * grid._grid.time_step * 1e15} fs")
        axes[0][0].legend(["Detector profile"])
    elif data.ndim == 5:
        # 绘制 2D 颜色图
        im = axes[0][0].imshow(bd.transpose(bd.squeeze(data[time_step_max_field, :, :, :, field_axis])), cmap="viridis", aspect="auto", origin="lower")
        # 添加颜色条
        plt.colorbar(im, ax=axes[0][0])
        # 设置标题和标签
        axes[0][0].set_title("Space distribution")
        if detector.axis == "x":
            axes[0][0].set_xlabel("Y")
            axes[0][0].set_ylabel("Z")
        if detector.axis == "y":
            axes[0][0].set_xlabel("X")
            axes[0][0].set_ylabel("Z")
        if detector.axis == "z":
            axes[0][0].set_xlabel("X")
            axes[0][0].set_ylabel("Y")
        # axes[0][0].set_xticks()  # 每隔10个显示一个刻度
        axes[0][0].set_title(f"Space distribution of {name_det} at {time_step_max_field * grid._grid.time_step * 1e15} fs")
        axes[0][0].legend(["Detector profile"])


    # 右侧子图: Time Signal 图
    if data.ndim == 3:
        axes[0][1].plot(time, data[:, index, 0], label="Ex")
        axes[0][1].plot(time, data[:, index, 1], label="Ey")
        axes[0][1].plot(time, data[:, index, 2], label="Ez")
    else:
        axes[0][1].plot(time, data[:, index_3d[0], index_3d[1], index_3d[2], 0], label="Ex")
        axes[0][1].plot(time, data[:, index_3d[0], index_3d[1], index_3d[2], 1], label="Ey")
        axes[0][1].plot(time, data[:, index_3d[0], index_3d[1], index_3d[2], 2], label="Ez")
    axes[0][1].set_xlabel('fs')
    axes[0][1].set_ylabel("E (V/m)")
    axes[0][1].set_title(f"Time Signal of {name_det}")
    axes[0][1].legend()

    # Spectrum
    axes[1][0].plot(spectrum_freqs * 1e-12, abs(spectrum))
    axes[1][0].set_xlabel('frequency (THz)')
    axes[1][0].set_ylabel(f"|E{conversions.number_to_letter(field_axis)}| (V/m)")
    axes[1][0].set_title(f"Spectrum of {name_det}")

    axes[1][1].plot(constants.c / spectrum_freqs * 1e6, abs(spectrum))
    axes[1][1].set_xlabel('wavelength (um)')
    axes[1][1].set_ylabel(f"|E{conversions.number_to_letter(field_axis)}| (V/m)")
    axes[1][1].set_title(f"Spectrum of {name_det}")

    plt.tight_layout()

    file_name = f"{name_det} profile"
    plt.savefig(os.path.join(grid.folder, f"{file_name}.png"))

    plt.close()

    return spectrum_freqs * 1e-12, spectrum

def visualize_detectors(grid,
                      field_axis="x",
                      field="E"):
    """
    绘制所有监视器的频谱。Draw the spectrum of all detectors.
    @param field_axis: "x", "y", "z"
    @param field: ”E"或"H"
    NOTE：
        This function will plot the spectrum of all detectors in the grid by
        using visualize_single_detector() for each one.
        这个函数使用 visualize_single_detector() 绘制网格中所有监视器的频谱。
    """
    # TODO: axis参数与其他可视化参数一致
    if field_axis is not None:
        field_axis = conversions.letter_to_number(field_axis)
    # spectrums = bd.empty(grid._grid.detectors.shape)
    # names = bd.empty(grid._grid.detectors.shape)
    for d in grid._grid.detectors:
        freqs, spectrum = visualize_single_detector(grid=grid, detector=d, field=field, field_axis=field_axis)
        plt.plot(freqs, abs(spectrum), linestyle='-', label=d.name)
    source, __, spectrum_source = grid.source_data()
    spectrum_source = abs(spectrum_source)
    plt.plot(freqs, spectrum_source, linestyle='-', label=source.name)

    plt.ylabel('%s%s' % (field, conversions.number_to_letter(field_axis)))
    plt.xlabel("frequency (THz)")
    plt.title("Spectrum of detectors")
    plt.legend()
    file_name = "Spectrum of detectors"
    plt.savefig(os.path.join(grid.folder, f"{file_name}.png"))
    plt.close()

def visualize(grid, axis: object = None, axis_index: int = None, field: str = "E", field_axis: str = None) -> None:
    """
    Generally visualize the grid, including field, energy, and detector data.
    可视化仿真结果，包括折射率分布，场分布，频谱和所有监视器结果。
    @param axis: axis to visualize, e.g., "x", "y", "z". If None, it will automatically detect.
    @param axis_index: int, the index of the axis to visualize. If None, it will be set to the middle of the axis.
    @param field: "E" or "H", the field to visualize. Default is "E".
    @param field_axis: str, the axis of the field to visualize, e.g., "x", "y", "z". If None, it will use the source's polarization.
    """
    # TODO: wl 能自动找到脉冲范围
    if axis is None:
        # 自动检测要绘制的维度
        dims_with_size_one = [i for i, size in enumerate(grid._grid.inverse_permittivity.shape) if size == 1]
        axis = conversions.number_to_letter(dims_with_size_one[0] if dims_with_size_one else 1)

    axis_index = axis_index or grid._grid.inverse_permittivity.shape[conversions.letter_to_number(axis)] // 2

    # 获取 source 数据
    for s in grid._grid.sources:
        source, _, _ = grid.source_data(source_name=s.name)

    # 获取 field_axis
    if field_axis is None:
        if grid._grid.sources:
            field_axis = getattr(source, "polarization", None)
        if field_axis is None:
            print("Grid.visualize: No source found in grid")

    save_fig(grid=grid, axis=axis, axis_index=axis_index)
    save_fig(grid=grid, axis=axis, axis_index=axis_index, show_energy=True)
    plot_n(grid=grid, axis=axis, axis_index=axis_index)
    plot_field(grid=grid, field=field, field_axis=field_axis, axis=axis, axis_index=axis_index)

    if grid._grid.detectors:  # 检查是否为空
        visualize_detectors(grid=grid, field_axis=field_axis, field=field)

        for detector in grid._grid.detectors:
            # grid.detector_profile(detector_name=detector.name, field=field, field_axis=field_axis)
            # grid.plot_fieldtime(grid=grid, field=field, field_axis=field_axis, name_det=detector.name)
            if isinstance(detector, BlockDetector):
                dB_map(grid=grid, field=field, field_axis=field_axis)
            # grid.calculate_Transmission(detector_name=detector.name, source_name=grid._try_to_find_source().name)



#
# def dump_to_vtk(pcb, filename, iteration, Ex_dump=False, Ey_dump=False, Ez_dump=False, Emag_dump=True, objects_dump=True, ports_dump=True):
#     '''
#     Floris
#     Extension is automatically chosen, you don't need to supply it
#
#     thanks
#     https://pyscience.wordpress.com/2014/09/06/numpy-to-vtk-converting-your-numpy-arrays-to-vtk-arrays-and-files/
#     https://bitbucket.org/pauloh/pyevtk/src/default/src/hl.py
#
#     Paraview needs a threshold operation to view the objects correctly.
#
#
#     argument scaling_factor=None,True(epsilon and hbar), or Float, to accomodate reduced units
#     or maybe
#     '''
