#!/usr/bin/env runaiida
"""Examplary script to submit a SkeafCalculation."""
# pylint: disable=unused-import
from aiida import engine, orm

from aiida_skeaf.calculations import SkeafCalculation
from aiida_skeaf.calculations.functions import create_bxsf_from_file


def submit():
    """Submit a SkeafCalculation."""

    # Create a RemoteData from a bxsf file
    # remote_path = orm.Str('/scratch/jqiao/filtered-PdCoO2-SO-band47.bxsf')
    # computer = orm.Str('localhost')
    # remote = create_bxsf_from_file(remote_path, computer)
    # Or load it
    remote = orm.load_node(137231)

    skeaf_code = orm.load_code("skeaf@localhost")

    parameters = {
        "fermi_energy": 14.2832,
        "num_interpolation": 50,  # 150,
        "theta": 0.000000,
        "phi": 0.000000,
        "h_vector_direction": "r",
        "min_extremal_frequency": 0.0147,
        "max_orbit_frequency_diff": 0.01,
        "max_orbit_coordinate_diff": 0.05,
        "near_wall_orbit": False,
        "starting_theta": 0.000000,
        "ending_theta": 90.000000,
        "starting_phi": 0.000000,
        "ending_phi": 90.000000,
        "num_rotation": 90,
    }

    inputs = {
        "code": skeaf_code,
        "parameters": parameters,
        "bxsf": remote,
        # "metadata": {
        #     "description": "Test job submission with the aiida_skeaf plugin",
        # },
    }

    result = engine.submit(SkeafCalculation, **inputs)

    print(f"{result}")


if __name__ == "__main__":
    submit()
