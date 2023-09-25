#!/usr/bin/env runaiida
"""Submit a wan2skeaf calculation with cold smearing."""
# pylint: disable=unused-import

from aiida import engine, orm

from aiida_skeaf.calculations.wan2skeaf import Wan2skeafCalculation


def submit():
    """Submit a Wan2skeafCalculation."""

    bxsf = orm.load_node(152164)

    wan2skeaf_code = orm.load_code("skeaf-wan2skeaf@localhost-slurm")

    parameters = {
        "num_electrons": 31,
        "band_index": "all",
        "smearing_type": "cold",
        "smearing_value": 0.13605693122994,
    }

    inputs = {
        "code": wan2skeaf_code,
        "parameters": parameters,
        "bxsf": bxsf,
        "bxsf_filename": "nscf.bxsf",
        "settings": dict({"autolink_bxsf_filename": "nscf.bxsf"}),
    }

    calc = engine.submit(Wan2skeafCalculation, **inputs)

    print(f"Submitted {calc}")

    calc.base.extras.set("smearing_type", parameters["smearing_type"])
    calc.base.extras.set("smearing_value", parameters["smearing_value"])


if __name__ == "__main__":
    submit()
