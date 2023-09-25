#!/usr/bin/env runaiida
"""Example script to submit two SkeafWorkChain with SOC, and plot frequency."""
from aiida import engine, orm

from aiida_wannier90_workflows.utils.workflows.builder.serializer import print_builder

from aiida_skeaf.utils.plot import plot_frequency_workchain
from aiida_skeaf.workflows import SkeafWorkChain


def submit():
    """Submit a SkeafWorkChain."""

    # Create a RemoteData from a BXSF file.
    # from aiida_skeaf.calculations.functions import create_bxsf_from_file
    # w90_calc = orm.load_node(5045)
    # bxsf = w90_calc.outputs.remote_folder
    # bxsf = create_bxsf_from_file(orm.Str('/home/jqiao/Documents/sdh/w90_5628.bxsf'), orm.Str('localhost'))
    # Load the created RemoteData
    bxsf = orm.load_node(137614)

    codes = {
        "wan2skeaf": "skeaf-wan2skeaf@localhost",
        "skeaf": "skeaf-skeaf@localhost",
    }

    # PdCoO2
    nelec_pw = 47
    num_exclude_bands = 20
    num_electrons = nelec_pw - num_exclude_bands

    # default is [001] to [100]
    builder = SkeafWorkChain.get_builder_from_protocol(
        codes,
        bxsf=bxsf,
        num_electrons=num_electrons,
        protocol="precise",
    )
    # SOC
    params = builder.wan2skeaf.parameters.get_dict()
    params["num_spin"] = 1
    builder.wan2skeaf.parameters = orm.Dict(dict=params)

    # [110] to [001]
    params = builder.skeaf.parameters.get_dict()
    params["starting_theta"] = 90.0
    params["ending_theta"] = 0.0
    params["starting_phi"] = 45.0
    params["ending_phi"] = 45.0
    builder.skeaf.parameters = orm.Dict(dict=params)

    print_builder(builder)

    wkchain = engine.submit(builder)

    print(f"Submitted {wkchain}")

    # Once workchain has finished, plot frequency vs angle
    # plot_frequency_workchain(wkchain, x="theta")


def plot_frequency():
    """Once workchain has finished, plot frequency vs angle."""
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(1, 2, sharey=True)
    # No gap
    fig.subplots_adjust(wspace=0)

    ax = axs[0]
    title = "[001] -> [100]"
    wkchain = orm.load_node(137663)
    plot_frequency_workchain(wkchain, x="theta", ax=ax)
    title = f"{ax.get_title()}\n{title}"
    ax.set_title(title)
    ax.set_xlim((0, 90))

    ax = axs[1]
    title = "[110] -> [001]"
    wkchain = orm.load_node(137710)
    plot_frequency_workchain(wkchain, x="theta", ax=ax)
    title = f"{ax.get_title()}\n{title}"
    ax.set_title(title)
    ax.set_xlim((90, 0))
    ax.set_ylabel(None)

    # Fermi energy
    params = wkchain.outputs.wan2skeaf.output_parameters.get_dict()
    fermi_scf = params["fermi_energy_in_bxsf"]
    fermi_mesh = params["fermi_energy_computed"]
    plt.suptitle(f"Ef_scf = {fermi_scf:.4f}eV, Ef_bxsf = {fermi_mesh:.4f}eV")

    plt.show()


if __name__ == "__main__":
    # submit()
    plot_frequency()
