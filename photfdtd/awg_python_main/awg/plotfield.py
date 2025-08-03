from .core import *
import matplotlib.pyplot as plt
import numpy as np
from . import *
from .field import Field


def plotfield(X, Y=[], **kwargs):
    """
    PLOTFIELD(X,Y) will plot Y as a function of X such that if Y is a
    complex quantity, the real part will be plotted to the left y-axis and
    the imaginary part to the secondary y-axis.

    PLOTFIELD(F) will plot a Field object according to its configuration.
    If the field is a scalar field, subplots will be produced for the
    electric and/or magnetic fields included. If the field is a vector
    field, those subplots will be broken up into individual component
    fields. If the field is two-dimensional, the plots become heat maps
    with the imaginary part ploted in overlaid contours.

    PLOTFIELD(__, NAME, VALUE) set options using one or more NAME, VALUE
    pairs from the following set:
    'PlotPhase' - When this option is set, each field plot will show the
                square of the modulus |U|^2 on the left axis and the phase
                in radians on the right axis, instead of the real and
                imaginary parts.
    'PlotPower' - When this option is set, one more subplot is added to
                show the field power density (Poynting vector). If the
                field only contains the electric or magnetic part alone,
                the plot features the field intensity instead.
    """

    _in = kwargs.keys()

    PlotPhase = kwargs["PlotPhase"] if "PlotPhase" in _in else False
    PlotPower = kwargs["PlotPower"] if "PlotPower" in _in else False
    UnwrapPhase = kwargs["UnwrapPhase"] if "UnwrapPhase" in _in else False
    NormalizePhase = kwargs["NormalizePhase"] if "NormalizePhase" in _in else False
    Figure = kwargs["Figure"] if "Figure" in _in else None

    if isinstance(X, Field):
        F = X
    else:
        F = Field(X, Y)

    rows = 1
    if F.isElectroMagnetic():
        rows = 2
    if PlotPower:
        rows += 1

    fig = Figure if Figure else plt.figure()

    def plotField1D(x, u, xname, uname, subplot_position):
        ax1 = fig.add_subplot(subplot_position)
        ax2 = ax1.twinx()
        ax1.set_xlabel(f"{xname}($\mu$m)")

        if PlotPhase:
            u1 = np.abs(u) ** 2
            u2 = np.angle(u)
            if UnwrapPhase:
                u2 = np.unwrap(u2)
            if NormalizePhase:
                u2 /= np.pi
            u1label = f"|{uname}|$^2$"
            u2label = f"$\phi$({uname})"
        else:
            u1 = np.real(u)
            u2 = np.imag(u)
            u1label = f"Re({uname})"
            u2label = f"Im({uname})"

        if PlotPhase and NormalizePhase:
            meany = np.mean(u2)
            miny = meany + min(-1, min(u2) - meany)
            maxy = meany + max(1, max(u2) - meany)
            ax2.set_ylim(miny, maxy)
            u2label = "$\\frac{\phi}{\pi}$" + f"({uname})"

        ax1.plot(x, u1, color="b")
        ax1.set_ylabel(u1label)
        ax2.plot(x, u2, color="r")
        ax2.set_ylabel(u2label)

    def plotField2D(x, y, u, xname, yname, uname):
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        cmap = plt.get_cmap("jet")

        if PlotPhase:
            u1 = np.abs(u) ** 2
            u2 = np.angle(u)
            if UnwrapPhase:
                u2 = np.unwrap(u2)
            if NormalizePhase:
                u2 /= np.pi
            utitle = f"|{uname}|$^2$"
            u2title = f"$\\phi$({uname})"
        else:
            u1 = np.real(u)
            u2 = np.imag(u)
            utitle = f"Re({uname})"
            u2title = f"Im({uname})"

        im = ax1.pcolormesh(x, y, u1, cmap=cmap)
        fig.colorbar(im, ax=ax1)
        cf = ax2.contourf(x, y, u2, cmap=cmap)
        fig.colorbar(cf, ax=ax2)

        ax1.set_title(utitle)
        ax1.set_xlabel(f"{xname}($\mu$m)")
        ax1.set_ylabel(f"{yname}($\mu$m)")
        ax2.set_title(u2title)
        ax2.set_xlabel(f"{xname}($\mu$m)")
        ax2.set_ylabel(f"{yname}($\mu$m)")

    if not F.isBidimensional():
        a = F.x
        t = "x"
        if F.hasY():
            a = F.y
            t = "y"

        if F.isScalar():
            if F.hasElectric():
                plotField1D(a, F.E, t, "E", rows * 100 + 10 + 1)
            if F.hasMagnetic():
                i = 0
                if F.hasElectric():
                    i = 1
                plotField1D(a, F.H, t, "H", rows * 100 + 10 + i + i)
        else:
            r = rows * 100 + 30
            if F.hasElectric():
                plotField1D(a, F.Ex, t, "E$_x$", r + 1)
                plotField1D(a, F.Ey, t, "E$_y$", r + 2)
                plotField1D(a, F.Ez, t, "E$_z$", r + 3)
            if F.hasMagnetic():
                i = 0
                if F.hasElectric():
                    i = 3
                plotField1D(a, F.Hx, t, "H$_x$", r + 1 + i)
                plotField1D(a, F.Hy, t, "H$_y$", r + 2 + i)
                plotField1D(a, F.Hz, t, "H$_z$", r + 3 + i)

    plt.tight_layout()
