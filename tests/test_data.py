""" Tests for calculations."""
import re

import pytest

from aiida_skeaf.data import InputParameters, SkeafParameters


def test_input_parameters_filename():
    """Test ``InputParameters`` raise exception when ``filename`` is provided."""
    from voluptuous.error import MultipleInvalid

    with pytest.raises(
        MultipleInvalid, match=re.escape("extra keys not allowed @ data['filename']")
    ):
        InputParameters(
            {
                "filename": "band46.bxsf",
            }
        ).get_dict()


def test_input_parameters_optional(data_regression, generate_input_parameters):
    """Test ``InputParameters`` can generate optional parameters."""
    inputs = InputParameters(generate_input_parameters(full=False)).get_dict()
    data_regression.check(inputs)


def test_skeaf_parameters(file_regression, generate_input_parameters):
    """Test ``SkeafParameters`` can generate the raw input for SKEAF."""
    inputs = SkeafParameters(generate_input_parameters(full=True)).generate()

    file_regression.check(inputs, encoding="utf-8", extension=".in")
