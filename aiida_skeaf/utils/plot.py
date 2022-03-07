#!/usr/bin/env python
"""Functions to plot output results."""
import matplotlib.pyplot as plt

from aiida import orm
from aiida.common import AttributeDict

from aiida_skeaf.calculations import SkeafCalculation
from aiida_skeaf.workflows import SkeafWorkChain


def plot_frequency(
    frequency: orm.ArrayData,
    x: str = "phi",
    y: str = "freq",
    label: str = None,
    ax: plt.Axes = None,
) -> None:
    """Plot ``SkeafCalculation.outputs.frequency`` array.

    :param frequency: ``SkeafCalculation.outputs.frequency``
    :type frequency: orm.ArrayData
    :param x: the array to be used as x data, defaults to "phi"
    :type x: str, optional
    :param y: the array to be used as y data, defaults to "freq"
    :type y: str, optional
    :param ax: If provided reuse this matplotlib axes, defaults to None
    :type ax: matplotlib.pyplot.Axes, optional
    """
    if any(_ not in frequency.get_arraynames() for _ in [x, y]):
        raise ValueError(f"valid x and y are {frequency.get_arraynames()}")

    x_array = frequency.get_array(x)
    y_array = frequency.get_array(y)

    header = frequency.attributes["header"].strip().split(",")

    show_plot = False
    if ax is None:
        _, ax = plt.subplots(1, 1)
        show_plot = True

    ax.plot(x_array, y_array)
    ax.scatter(
        x_array,
        y_array,
        marker="o",
        facecolors="none",
        edgecolors="r",
        label=label,
    )

    xlabel = [_ for _ in header if x in _.lower()][0]
    ylabel = [_ for _ in header if y in _.lower()][0]

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title("Frequency vs angle")

    if show_plot:
        plt.show()


def plot_frequency_calc(
    calc: SkeafCalculation,
    **kwargs,
) -> None:
    """Plot SKEAF output frequency vs angle.

    :param calc: A finished ``SkeafCalculation``
    :type calc: SkeafCalculation
    """
    frequency: orm.ArrayData = calc.outputs.frequency

    plot_frequency(frequency=frequency, **kwargs)


def plot_frequency_workchain(
    wkchain: SkeafWorkChain,
    **kwargs,
) -> None:
    """Plot SKEAF output frequency vs angle.

    :param wkchain: A finished ``SkeafWorkChain``
    :type wkchain: SkeafWorkChain
    """
    show_plot = False
    if "ax" not in kwargs:
        _, ax = plt.subplots()
        show_plot = True
    else:
        ax = kwargs.pop("ax")

    skeaf_outputs: AttributeDict = wkchain.outputs.skeaf
    # Sort by band index
    skeaf_outputs = dict(sorted(skeaf_outputs.items(), key=lambda _: _[0]))

    for band_idx, skeaf_out in skeaf_outputs.items():
        frequency: orm.ArrayData = skeaf_out.frequency

        plot_frequency(frequency=frequency, label=band_idx, ax=ax, **kwargs)

    ax.set_title(f"{wkchain.process_label}<{wkchain.pk}>")
    ax.legend()

    if show_plot:
        plt.show()
