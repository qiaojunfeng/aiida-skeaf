#!/usr/bin/env runaiida
"""Examplary script to submit a SkeafCalculation."""
# pylint: disable=unused-import
import pathlib

from aiida import engine, orm

from aiida_skeaf.calculations import SkeafCalculation
from aiida_skeaf.calculations.functions import create_bxsf_from_file

INPUT_DIR = pathlib.Path(__file__).absolute().parent / "input_files"


def submit():
    """Submit a SkeafCalculation."""

    # Create a RemoteData from a bxsf file
    remote_path = orm.Str(str(INPUT_DIR / "cylinder.bxsf"))
    computer = orm.Str("localhost")
    bxsf = create_bxsf_from_file(remote_path, computer)
    # Or load it
    # bxsf = orm.load_node(137231)

    skeaf_code = orm.load_code("skeaf@localhost")

    parameters = {
        "fermi_energy": 0.086887,
        "num_interpolation": 50,
        "theta": 0.000000,
        "phi": 0.000000,
        "h_vector_direction": "r",
        "min_extremal_frequency": 0.01,
        "max_orbit_frequency_diff": 0.01,
        "max_orbit_coordinate_diff": 0.05,
        "near_wall_orbit": False,
        "starting_theta": 0.000000,
        "ending_theta": 0.000000,
        "starting_phi": 0.000000,
        "ending_phi": 90.000000,
        "num_rotation": 90,
    }

    inputs = {
        "code": skeaf_code,
        "parameters": parameters,
        "bxsf": bxsf,
    }

    calc = engine.submit(SkeafCalculation, **inputs)

    print(f"Submitted {calc}")

    # Once finished, plot the frequency vs angle
    # from aiida_skeaf.utils.plot import plot_frequency
    # plot_frequency(calc)


if __name__ == "__main__":
    submit()
