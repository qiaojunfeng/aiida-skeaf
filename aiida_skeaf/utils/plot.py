#!/usr/bin/env python
"""Functions to plot output results."""
import matplotlib.pyplot as plt

from aiida import orm
from aiida.plugins import CalculationFactory

SkeafCalculation = CalculationFactory("skeaf.skeaf")


def plot_frequency(
    calc: SkeafCalculation,
    x: str = "phi",
    y: str = "freq",
) -> None:
    """Plot SKEAF output frequency vs angle.

    :param calc: A finished ``SkeafCalculation``
    :type calc: SkeafCalculation
    :param x: the array to be used as x data, defaults to 'phi'
    :type x: str
    :param y: the array to be used as y data, defaults to 'freq'
    :type y: str
    :raises ValueError: if ``x`` or ``y`` not in ``calc.outputs.frequency.get_arraynames()``
    """
    frequency: orm.ArrayData = calc.outputs.frequency

    if any(_ not in frequency.get_arraynames() for _ in [x, y]):
        raise ValueError(f"valid x and y are {frequency.get_arraynames()}")

    x_array = frequency.get_array(x)
    y_array = frequency.get_array(y)

    header = frequency.attributes["header"].strip().split(",")

    _, ax = plt.subplots(1, 1)

    ax.plot(x_array, y_array)
    ax.scatter(x_array, y_array, marker="o", facecolors="none", edgecolors="r")

    xlabel = [_ for _ in header if x in _.lower()][0]
    ylabel = [_ for _ in header if y in _.lower()][0]

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title("Frequency vs angle")

    plt.show()
