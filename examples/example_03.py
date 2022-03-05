#!/usr/bin/env runaiida
"""Examplary script to submit a SkeafWorkChain."""
from aiida import engine, orm

from aiida_wannier90_workflows.utils.workflows.builder import print_builder

from aiida_skeaf.utils.plot import plot_frequency_workchain
from aiida_skeaf.workflows import SkeafWorkChain


def submit():
    """Submit a SkeafWorkChain."""

    bxsf = orm.load_node(137298)

    codes = {
        "wan2skeaf": "skeaf-wan2skeaf@localhost",
        "skeaf": "skeaf@localhost",
    }

    builder = SkeafWorkChain.get_builder_from_protocol(
        codes,
        bxsf=bxsf,
        num_electrons=2,
        protocol="fast",
    )

    print_builder(builder)

    wkchain = engine.submit(builder)

    print(f"Submitted {wkchain}")

    # Once workchain has finished, plot frequency vs angle
    plot_frequency_workchain(wkchain, x="theta")


if __name__ == "__main__":
    submit()
