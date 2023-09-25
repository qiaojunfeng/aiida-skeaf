#!/usr/bin/env runaiida
"""Submit a wan2skeaf calculation using create_wan2skeaf_builder function."""
# pylint: disable=unused-import

from aiida import engine, orm

from aiida_skeaf.utils import create_wan2skeaf_builder


def submit():
    """Submit a Wan2skeafCalculation."""

    bxsf = orm.load_node(152164)

    wan2skeaf_code = orm.load_code("skeaf-wan2skeaf@localhost-slurm")

    parameters = {
        "num_electrons": 31,
        "band_index": "all",
    }

    inputs = {
        "code": wan2skeaf_code,
        "parameters": parameters,
        "bxsf": bxsf,
        "bxsf_filename": "nscf.bxsf",
        "settings": dict({"autolink_bxsf_filename": "nscf.bxsf"}),
    }

    builder = create_wan2skeaf_builder(parameters, inputs)
    calc = engine.submit(builder)

    print(f"Submitted {calc}")


if __name__ == "__main__":
    submit()
