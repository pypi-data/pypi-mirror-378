import os
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import latdraw
import latdraw.interfaces as interfaces
from latdraw import lattice


def _get_lattice(lattice_or_path_to_one) -> lattice.Beamline:
    try:
        fpath = os.fspath(lattice_or_path_to_one)
    except TypeError:
        lattice = lattice_or_path_to_one
    else:
        return latdraw.read(fpath)

    try:
        lattice = interfaces.madx_twiss_to_beamline(lattice_or_path_to_one)
    except:
        pass

    return lattice


def subplots_with_lattice(
    lattice: Union[str, lattice.Beamline, pd.DataFrame],
    s_offset=0,
    nrows: int = 1,
    gridspec_kw=None,
    **kwargs,
):
    # height_ratios = [1, 0.5, 0.5, 1]
    # the_gridspec_kw = {"height_ratios": height_ratios,
    #                    "hspace": 0.05}
    # if gridspec_kw is None:
    #     gridspec_kw = {}
    # the_gridspec_kw |= gridspec_kw

    # Plot goes at the top
    pattern = [lattice]
    pattern.extend(nrows * [None])
    return subplots_with_lattices(pattern, s_offset=s_offset, **kwargs)


def subplots_with_lattices(
    pattern, s_offset=0, **draw_kwargs
) -> tuple[plt.Figure, list[plt.Axes]]:
    pattern = np.array(pattern, dtype=object)

    height_ratios = np.full_like(pattern, 1.0, dtype=float)
    # Get indices of where machines should be plotted
    indices = [index for (index, value) in enumerate(pattern) if value is not None]
    height_ratios[indices] = 0.25

    the_gridspec_kw = {"height_ratios": height_ratios, "hspace": 0.05}

    fig, axes = plt.subplots(
        nrows=len(pattern), sharex=True, gridspec_kw=the_gridspec_kw
    )

    for lattice, ax in zip(pattern, axes):
        if lattice is None:
            continue

        lattice = _get_lattice(lattice)
        latdraw.draw(fig, ax, lattice, s_offset=s_offset, **draw_kwargs)

        ax.set_yticks([], [])

        ax.tick_params(
            top=False,
            bottom=False,
            left=False,
            right=False,
            labelleft=False,
            labelbottom=False,
        )

        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # ax.spines['top'].set_visible(True)
        # ax.spines['bottom'].set_visible(False)

        ax.set_ylim(-0.25, 0.25)

    return fig, axes


def plot_optics(beamline, s, betax, betay):
    fig, (mx, axbx) = latdraw.subplots_with_lattice(beamline, nrows=1)

    axbx.plot(s, betax, label=r"$x$")
    axbx.plot(s, betay, label=r"$y$")

    axbx.legend()
    axbx.set_xlabel("$s$ / m")
    axbx.set_ylabel(r"$\beta_{x,y}$ / m")


def plot_optics(some_beamline, some_optics, title=""):
    bl = interfaces.coerce_beamline(some_beamline)
    optics = latdraw.optics.coerce_optics(some_optics)

    fig, axes = subplots_with_lattice(bl, nrows=2)

    fig, (mx, ax1, ax2) = fig, axes

    ax1.plot(optics.s, optics.beta_x, label=r"$\beta_x$")
    ax1.plot(optics.s, optics.beta_y, label=r"$\beta_y$")
    ax1.legend()
    beta_label(ax1)

    ax2.plot(optics.s, optics.dx, label=r"$D_x$")
    ax2.plot(optics.s, optics.dy, label=r"$D_y$")
    dispersion_label(ax2)
    s_label(ax2)
    ax2.legend()

    mx.set_title(title)

    return fig, axes


def simple_figure(
    some_beamline, title="", **drawkwargs
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    bl = interfaces.coerce_beamline(some_beamline)

    fig, axes = subplots_with_lattice(bl, nrows=1, **drawkwargs)
    s_label(axes[-1])
    axes[0].set_title(title)
    # fig.suptitle(title)
    return fig, axes


def two_axes_figure(
    some_beamline, title=""
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes]]:
    bl = interfaces.coerce_beamline(some_beamline)

    fig, axes = subplots_with_lattice(bl, nrows=2)
    s_label(axes[-1])
    axes[0].set_title(title)
    # fig.suptitle(title)
    return fig, axes


def three_axes_figure(
    some_beamline, title=""
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes, plt.Axes]]:
    bl = interfaces.coerce_beamline(some_beamline)

    fig, axes = subplots_with_lattice(bl, nrows=3)
    s_label(axes[-1])
    axes[0].set_title(title)
    return fig, axes


def four_axes_figure(
    some_beamline, title=""
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes, plt.Axes]]:
    bl = interfaces.coerce_beamline(some_beamline)

    fig, axes = subplots_with_lattice(bl, nrows=4)
    s_label(axes[-1])
    axes[0].set_title(title)
    return fig, axes


def beta_label(ax, subscript=""):
    if not subscript:
        ax.set_ylabel(r"$\beta$ / m")
    else:
        ax.set_ylabel(rf"$\beta_{subscript}$ / m")


def alpha_label(ax, subscript=""):
    if not subscript:
        ax.set_ylabel(r"$\alpha$ / m")
    else:
        ax.set_ylabel(rf"$\alpha_{subscript}$")


def dispersion_label(ax, subscript=""):
    if not subscript:
        ax.set_ylabel(r"$D$ / m")
    else:
        ax.set_ylabel(rf"$D_{{{subscript}}}$ / m")


def s_label(ax) -> None:
    ax.set_xlabel(r"$s$ / m")


def energy_label(ax, unit="GeV"):
    ax.set_ylabel(f"$E$ / {unit}")


def draw_vline(axes: list[plt.Axes], x: float, **vline_kwargs) -> None:
    for ax in axes:
        ax.axvline(x, **vline_kwargs)


def compare_two_optics(
    some_beamline1,
    optics1,
    some_beamline2,
    optics2,
    label1="",
    label2="",
    title="",
    dimension="x",
):
    bl1 = interfaces.coerce_beamline(some_beamline1)
    optics1 = latdraw.optics.coerce_optics(optics1)

    bl2 = interfaces.coerce_beamline(some_beamline2)
    optics2 = latdraw.optics.coerce_optics(optics2)

    fig, axes = subplots_with_lattice(bl1, nrows=2)
    fig, (mx, ax1, ax2) = fig, axes

    (l1,) = ax1.plot(optics1.s, optics1[f"beta_{dimension}"], label=label1)
    beta_label(ax1)

    ax1.plot(
        optics2.s, optics2[f"beta_{dimension}"], label=label2
    )  # color=l1.get_color(),
    # ax1.plot(optics2.s, optics2.beta_y)
    if label1 or label2:
        ax1.legend()

    (l1,) = ax2.plot(optics1.s, optics1[f"alpha_{dimension}"])
    (l1,) = ax2.plot(optics2.s, optics2[f"alpha_{dimension}"])

    ax2.set_ylabel(rf"$\alpha_{dimension}$")

    beta_label(ax1, dimension)
    s_label(ax2)

    return fig, axes

    # ax2.plot(optics.s, optics.dx, label=r"$D_x$")
    # ax2.plot(optics.s, optics.dy, label=r"$D_y$")
    # dispersion_label(ax2)
    # s_label(ax2)
    # ax2.legend()
