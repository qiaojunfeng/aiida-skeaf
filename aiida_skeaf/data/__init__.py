"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""
# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from voluptuous import All, In, Optional, Required, Schema

# Allowed parameters of SkeafCalculation.inputs.parameters
input_parameters = {
    Required("fermi_energy"): float,
    Optional("num_interpolation", default=150): int,
    Required("theta"): float,
    Required("phi"): float,
    Required("h_vector_direction"): All(str, In(["a", "b", "c", "n", "r"])),
    Required("min_extremal_frequency"): float,
    Optional("max_orbit_frequency_diff", default=0.01): float,
    Optional("max_orbit_coordinate_diff", default=0.05): float,
    Optional("near_wall_orbit", default=False): bool,
    Required("starting_theta"): float,
    Required("ending_theta"): float,
    Required("starting_phi"): float,
    Required("ending_phi"): float,
    Optional("num_rotation", default=1): int,
    # For spherical coordinates (r, theta, phi), theta is the angle w.r.t to z-axis
    # in ISO convention, however in SKEAF, phi is the angle w.r.t to z-axis.
    # Setting this to False is the default behaviour of skeaf,
    # if set as True, I will exchange theta and phi when writting the raw input file
    # for skeaf.
    Optional("angle_iso_convention", default=False): bool,
    Optional("convert_fermi_energy_eV_to_Ry", default=False): bool,
}

# Allowed input paramters of skeaf config.in
skeaf_parameters = {
    Required("filename"): str,
    Required("fermi_energy"): float,
    Required("num_interpolation", default=150): int,
    Required("theta"): float,
    Required("phi"): float,
    Required("h_vector_direction"): All(str, In(["a", "b", "c", "n", "r"])),
    Required("min_extremal_frequency"): float,
    Required("max_orbit_frequency_diff", default=0.01): float,
    Required("max_orbit_coordinate_diff", default=0.05): float,
    Required("near_wall_orbit", default=False): bool,
    Required("starting_theta"): float,
    Required("ending_theta"): float,
    Required("starting_phi"): float,
    Required("ending_phi"): float,
    Optional("num_rotation", default=1): int,
}


class InputParameters:  # pylint: disable=too-many-ancestors
    """
    Command line options for diff.

    This class represents a python dictionary used to
    pass command line options to the executable.
    """

    # "voluptuous" schema  to add automatic validation
    schema = Schema(input_parameters)

    # pylint: disable=redefined-builtin
    def __init__(self, dict, /):
        """
        Constructor for the data class

        Usage: ``DiffParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        self.dict = self.validate(dict)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(DiffParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return self.schema(parameters_dict)

    def get_dict(self) -> dict:
        """Return validated dict."""
        return self.dict

    def __str__(self):
        return str(self.dict)


class SkeafParameters(InputParameters):  # pylint: disable=too-many-ancestors
    """
    Command line options for diff.

    This class represents a python dictionary used to
    pass command line options to the executable.
    """

    # "voluptuous" schema  to add automatic validation
    schema = Schema(skeaf_parameters)

    def generate(self) -> str:
        """Synthesize command line parameters."""
        inputs = []

        inputs.append(f"{self.dict['filename']:52s}| Filename (50 chars. max)")
        inputs.append(
            f"{self.dict['fermi_energy']:12.6f}" + " " * 40 + "| Fermi energy (Ryd)"
        )
        inputs.append(
            f"{self.dict['num_interpolation']:4d}"
            + " " * 48
            + "| Interpolated number of points per single side"
        )
        inputs.append(f"{self.dict['theta']:11.6f}" + " " * 41 + "| Theta (degrees)")
        inputs.append(f"{self.dict['phi']:11.6f}" + " " * 41 + "| Phi (degrees)")
        inputs.append(
            f"{self.dict['h_vector_direction']:1s}" + " " * 51 + "| H-vector direction"
        )
        inputs.append(
            f"{self.dict['min_extremal_frequency']:8.4f}"
            + " " * 44
            + "| Minimum extremal FS freq. (kT)"
        )
        inputs.append(
            f"{self.dict['max_orbit_frequency_diff']:7.3f}"
            + " " * 45
            + "| Maximum fractional diff. between orbit freqs. for averaging"
        )
        inputs.append(
            f"{self.dict['max_orbit_coordinate_diff']:7.3f}"
            + " " * 45
            + "| Maximum distance between orbit avg. coords. for averaging"
        )
        near_wall_orbit = "y" if self.dict["near_wall_orbit"] else "n"
        inputs.append(
            f"{near_wall_orbit:1s}"
            + " " * 51
            + "| Allow extremal orbits near super-cell walls?"
        )
        inputs.append(
            f"{self.dict['starting_theta']:11.6f}"
            + " " * 41
            + "| Starting theta (degrees)"
        )
        inputs.append(
            f"{self.dict['ending_theta']:11.6f}" + " " * 41 + "| Ending theta (degrees)"
        )
        inputs.append(
            f"{self.dict['starting_phi']:11.6f}" + " " * 41 + "| Starting phi (degrees)"
        )
        inputs.append(
            f"{self.dict['ending_phi']:11.6f}" + " " * 41 + "| Ending phi (degrees)"
        )
        inputs.append(
            f"{self.dict['num_rotation']:5d}" + " " * 47 + "| Number of rotation angles"
        )
        return "\n".join(inputs)

    def __str__(self):
        """String representation of node."""
        return self.generate()
