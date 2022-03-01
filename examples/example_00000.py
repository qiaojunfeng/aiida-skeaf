# #!/usr/bin/env python
# """Run a skeaf calculation on localhost.

# Usage: ./example_01.py
# """
# from os import path
# import warnings

# import click

# from aiida import cmdline, engine
# from aiida.plugins import CalculationFactory, DataFactory

# from aiida_skeaf import helpers

# INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), "input_files")


# def test_run(skeaf_code, bxsf):
#     """Run a calculation on the localhost computer.

#     Uses test helpers to create AiiDA Code on the fly.
#     """
#     if not skeaf_code:
#         # get code
#         computer = helpers.get_computer()
#         skeaf_code = helpers.get_code(
#             entry_point="skeaf.skeaf",
#             computer=computer,
#         )

#     # Prepare input parameters
#     parameters = {
#         "fermi_energy": 0.086887,
#         "num_interpolation": 50,
#         "theta": 0.000000,
#         "phi": 0.000000,
#         "h_vector_direction": "r",
#         "min_extremal_frequency": 0.01,
#         "max_orbit_frequency_diff": 0.01,
#         "max_orbit_coordinate_diff": 0.05,
#         "near_wall_orbit": False,
#         "starting_theta": 0.000000,
#         "ending_theta": 0.000000,
#         "starting_phi": 0.000000,
#         "ending_phi": 90.000000,
#         "num_rotation": 90,
#     }

#     # Prepare bxsf
#     if not bxsf:
#         # Create a RemoteData from a bxsf file
#         create_bxsf_from_file = CalculationFactory("skeaf.create_bxsf_from_file")
#         bxsf_file = path.join(INPUT_DIR, "cylinder.bxsf")
#         computer = skeaf_code.computer.label
#         if computer not in ["localhost", helpers.LOCALHOST_NAME]:
#             warnings.warn(
#                 f"Auto-created RemoteData for {bxsf_file} only works with localhost"
#             )
#         Str = DataFactory("str")
#         bxsf = create_bxsf_from_file(
#             remote_path=Str(bxsf_file),
#             computer=Str(computer),
#         )

#     # Set up calculation
#     inputs = {
#         "code": skeaf_code,
#         "parameters": parameters,
#         "bxsf": bxsf,
#         "metadata": {
#             "description": "Test job submission with the aiida_skeaf plugin",
#         },
#     }

#     SkeafCalculation = CalculationFactory("skeaf.skeaf")
#     calc = engine.submit(SkeafCalculation, **inputs)

#     print(f"Submitted {calc}")


# @click.command()
# @cmdline.utils.decorators.with_dbenv()
# @cmdline.params.options.CODE()
# @click.argument("bxsf", type=click.Path(exists=True))
# def cli(code, bxsf):
#     """Run example.

#     Example usage: $ ./example_01.py --code skeaf@localhost --bxsf aiida.bxsf

#     Alternative (creates skeaf_v1p3p0_r149@localhost-test code): $ ./example_01.py

#     Help: $ ./example_01.py --help
#     """
#     test_run(code, bxsf)


# if __name__ == "__main__":
#     cli()  # pylint: disable=no-value-for-parameter
