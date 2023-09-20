#!/usr/bin/env runaiida
"""Examplary script to submit a Wan2skeafCalculation."""
# pylint: disable=unused-import
from aiida import engine, orm

from aiida_skeaf.calculations.wan2skeaf import Wan2skeafCalculation


def submit():
    """Submit a Wan2skeafCalculation."""

    bxsf = orm.load_node(137298)

    # skeaf_code = orm.load_code("skeaf@localhost")
    wan2skeaf_code = orm.load_code("skeaf-wan2skeaf@localhost")

    parameters = {
        "num_electrons": 1,
        "band_index": "all",
    }

    inputs = {
        "code": wan2skeaf_code,
        "parameters": parameters,
        "bxsf": bxsf,
    }

    calc = engine.submit(Wan2skeafCalculation, **inputs)

    print(f"Submitted {calc}")


if __name__ == "__main__":
    submit()
