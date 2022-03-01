"""pytest fixtures for simplified testing."""
import pytest

from aiida import orm

pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]


@pytest.fixture(scope="function", autouse=True)
def clear_database_auto(clear_database):  # pylint: disable=unused-argument
    """Automatically clear database in between tests."""


@pytest.fixture(scope="function")
def fixture_sandbox():
    """Return a `SandboxFolder`."""
    from aiida.common.folders import SandboxFolder

    with SandboxFolder() as folder:
        yield folder


@pytest.fixture
def generate_calc_job():
    """Fixture to construct a new `CalcJob` instance and call `prepare_for_submission` for testing `CalcJob` classes.

    The fixture will return the `CalcInfo` returned by `prepare_for_submission` and the temporary folder that was passed
    to it, into which the raw input files will have been written.
    """

    def _generate_calc_job(folder, entry_point_name, inputs=None):
        """Fixture to generate a mock `CalcInfo` for testing calculation jobs."""
        from aiida.engine.utils import instantiate_process
        from aiida.manage.manager import get_manager
        from aiida.plugins import CalculationFactory

        manager = get_manager()
        runner = manager.get_runner()

        process_class = CalculationFactory(entry_point_name)
        process = instantiate_process(runner, process_class, **inputs)

        calc_info = process.prepare_for_submission(folder)

        return calc_info

    return _generate_calc_job


@pytest.fixture(scope="function")
def skeaf_code(aiida_local_code_factory):
    """Get a skeaf code."""
    return aiida_local_code_factory(executable="diff", entry_point="skeaf")


@pytest.fixture(scope="function")
def generate_bxsf_remotedata(aiida_localhost, tmp_path):
    """Get a skeaf code."""

    bxsf_filename = "aiida.bxsf"
    bxsf_file = tmp_path / bxsf_filename
    bxsf_file.write_text("w90 bxsf")

    remote_data = orm.RemoteData(remote_path=str(bxsf_file), computer=aiida_localhost)

    return remote_data


@pytest.fixture(scope="function")
def generate_input_parameters():
    """Get an input parameters for ``SkeafCalculation``."""

    def _generate_input_parameters(full: bool = False) -> dict:
        """Generate inputs.

        :param full: return a full parameters or a minimal set, defaults to False
        :type full: bool, optional
        :return: parameters
        :rtype: dict
        """
        if full:
            params = {
                "filename": "band46.bxsf",
                "fermi_energy": 14.2832,
                "num_interpolation": 150,
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
        else:
            params = {
                "fermi_energy": 14.2832,
                "theta": 0.000000,
                "phi": 0.000000,
                "h_vector_direction": "r",
                "min_extremal_frequency": 0.0147,
                "starting_theta": 0.000000,
                "ending_theta": 90.000000,
                "starting_phi": 0.000000,
                "ending_phi": 90.000000,
            }
        return params

    return _generate_input_parameters
