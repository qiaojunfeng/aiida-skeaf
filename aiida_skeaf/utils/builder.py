"""This module contains the builder functions for the calculations."""
import typing as ty

from aiida import orm

from aiida_skeaf.calculations import Wan2skeafCalculation


def create_wan2skeaf_builder(
    params: ty.Union[dict, orm.Dict], inputs: ty.Union[dict, orm.Dict]
):  # replace inputs with bxsf, bxsf_filename etc
    """Create a builder for the Wan2SkeafCalculation.
    :param params: the parameters dictionary
    :type params: dict, orm.Dict
    :param inputs: the inputs dictionary
    :type inputs: dict, orm.Dict
    :return: the builder
    :rtype:
    """
    builder = Wan2skeafCalculation.get_builder()
    builder.code = inputs["code"]
    builder.parameters = params
    builder.bxsf = inputs["bxsf"]
    builder.bxsf_filename = inputs["bxsf_filename"]
    builder.settings.autolink_bxsf_filename = inputs[  # pylint: disable=no-member
        "settings"
    ][
        "autolink_bxsf_filename"
    ]  # I kept this one here as my calculations were failing without it
    # set settings ouside of this function
    return builder


# in the submission script write a function that will create the builder from parent and call this function
