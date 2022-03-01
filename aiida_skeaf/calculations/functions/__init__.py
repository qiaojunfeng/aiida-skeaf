#!/usr/bin/env python
"""Helper calcfunctions."""
import pathlib
import typing as ty

from aiida import orm
from aiida.engine import calcfunction


@calcfunction
def create_bxsf_from_wannier90(remote_folder: orm.RemoteData) -> orm.RemoteData:
    """Create an ``RemoteData`` representing a single bxsf file from a ``Wannier90Calculation.outputs.remote_folder``.

    :param remote_folder: A ``RemoteData`` e.g. ``Wannier90Calculation.outputs.remote_folder``.
    :type remote_folder: aiida.orm.RemoteData
    :return: An ``RemoteData`` representing a single bxsf file, for ``SkeafCalculation.inputs.bxsf``.
    :rtype: aiida.orm.RemoteData
    """
    computer = remote_folder.computer
    remote_path = pathlib.Path(remote_folder.get_remote_path())

    bxsf_filename = "aiida.bxsf"
    if bxsf_filename not in remote_folder.listdir():
        raise ValueError(f"{remote_folder} does not contain {bxsf_filename}")

    remote_path /= bxsf_filename

    remote = orm.RemoteData(
        remote_path=str(remote_path),
        computer=computer,
    )

    return remote


@calcfunction
def create_bxsf_from_file(remote_path: orm.Str, computer: orm.Str) -> orm.RemoteData:
    """Create an ``RemoteData`` representing a single bxsf file from a file path.

    :param remote_path: An ``Str`` containing the path for a remote bxsf file.
    :type remote_path: aiida.orm.RemoteData
    :param computer: The label of remote computer (``calcfunction`` does not accept ``Computer`` as input).
    :type computer: aiida.orm.Str
    :return: An ``RemoteData`` representing a single bxsf file, for ``SkeafCalculation.inputs.bxsf``.
    :rtype: aiida.orm.RemoteData
    """

    remote = orm.RemoteData(
        remote_path=remote_path.value,
        computer=orm.load_computer(computer.value),
    )

    return remote
