#!/usr/bin/env python
"""Wrapper workchain for `SkeafCalculation` to automatically handle several errors."""
import pathlib
import typing as ty

from aiida_quantumespresso.utils.mapping import prepare_process_inputs
from aiida_quantumespresso.workflows.protocols.utils import ProtocolMixin

from aiida import orm
from aiida.common import AttributeDict
from aiida.common.lang import type_check
from aiida.engine import (
    PortNamespace,
    ProcessBuilder,
    ToContext,
    WorkChain,
    append_,
    while_,
)

from aiida_skeaf.calculations import SkeafCalculation, Wan2skeafCalculation

__all__ = ["validate_inputs", "SkeafWorkChain"]


def validate_inputs(
    inputs: AttributeDict, ctx=None  # pylint: disable=unused-argument
) -> None:
    """Validate the inputs of the entire input namespace."""


class SkeafWorkChain(ProtocolMixin, WorkChain):
    """Workchain to run `Wan2skeafCalculation` and `SkeafCalculation`.

    Given a wannier90 generated RemoteData containing a bxsf file,
    run skeaf on all the bands in the bxsf.

    """

    @classmethod
    def define(cls, spec) -> None:
        """Define the process spec."""

        super().define(spec)

        spec.input(
            "bxsf",
            valid_type=orm.RemoteData,
            help="Input BXSF file or the output remote_folder of Wannier90Calculation.",
        )
        spec.expose_inputs(
            Wan2skeafCalculation,
            namespace="wan2skeaf",
            exclude=("bxsf",),
            namespace_options={"help": "Inputs for the `Wan2skeafCalculation`."},
        )
        spec.expose_inputs(
            SkeafCalculation,
            namespace="skeaf",
            exclude=("bxsf",),
            namespace_options={"help": "Inputs for the `Wan2skeafCalculation`."},
        )
        spec.input(
            "clean_workdir",
            valid_type=orm.Bool,
            default=lambda: orm.Bool(False),
            serializer=orm.to_aiida_type,
            help="If `True`, work directories of all called calculation jobs will be cleaned at the end of execution.",
        )

        spec.inputs.validator = validate_inputs

        spec.expose_outputs(Wan2skeafCalculation, namespace="wan2skeaf")
        spec.output_namespace(
            "skeaf",
            dynamic=True,
            # valid_type=PortNamespace,
            help="Output SkeafCalculation for each band.",
        )

        spec.outline(
            cls.setup,
            cls.run_wan2skeaf,
            cls.inspect_wan2skeaf,
            while_(cls.should_run_skeaf)(
                cls.run_skeaf,
                cls.inspect_skeaf,
            ),
            cls.results,
        )

        spec.exit_code(
            401,
            "ERROR_SUB_PROCESS_FAILED_WAN2SKEAF",
            message="Unrecoverable error when running wan2skeaf.",
        )
        spec.exit_code(
            402,
            "ERROR_SUB_PROCESS_FAILED_SKEAF",
            message="Unrecoverable error when running skeaf.",
        )

    @classmethod
    def get_protocol_filepath(cls) -> pathlib.Path:
        """Return the ``pathlib.Path`` to the ``.yaml`` file that defines the protocols."""
        from importlib_resources import files

        from . import protocols

        return files(protocols) / "skeaf.yaml"

    @classmethod
    def get_builder_from_protocol(  # pylint: disable=too-many-statements
        cls,
        codes: ty.Dict[str, ty.Union[orm.Code, str, int]],
        *,
        bxsf: orm.RemoteData,
        num_electrons: int,
        protocol: str = None,
        overrides: dict = None,
    ) -> ProcessBuilder:
        """Return a builder prepopulated with inputs selected according to the chosen protocol.

        :param codes: [description]
        :type codes: ty.Dict[str, ty.Union[orm.Code, str, int]]
        :param bxsf: [description]
        :type bxsf: orm.RemoteData
        :param protocol: [description], defaults to None
        :type protocol: str, optional
        :param overrides: [description], defaults to None
        :type overrides: dict, optional
        :return: [description]
        :rtype: ProcessBuilder
        """
        from aiida_wannier90_workflows.utils.workflows.builder import (
            recursive_merge_builder,
        )

        required_codes = ["wan2skeaf", "skeaf"]
        if not all(_ in codes for _ in required_codes):
            raise ValueError(f"`codes` must contain {required_codes}")

        for key, code in codes.items():
            if not isinstance(code, orm.Code):
                codes[key] = orm.load_code(code)

        type_check(bxsf, orm.RemoteData)

        inputs = cls.get_protocol_inputs(protocol, overrides)

        inputs["wan2skeaf"]["code"] = codes["wan2skeaf"]
        inputs["skeaf"]["code"] = codes["skeaf"]
        inputs["bxsf"] = bxsf

        wan2skeaf_parameters = inputs["wan2skeaf"]["parameters"]
        wan2skeaf_parameters["num_electrons"] = num_electrons
        inputs["wan2skeaf"]["parameters"] = orm.Dict(dict=wan2skeaf_parameters)

        builder = cls.get_builder()
        builder = recursive_merge_builder(builder, inputs)

        return builder

    def setup(self) -> None:
        """Create context variables."""

        # A dict for remaning bxsf RemoteData to run SkeafCalculation, e.g.
        # {'band49': RemoteData, 'band48': RemoteData}
        self.ctx.bxsf_to_run = {}
        # A list of band that have finished, e.g.
        # ['band48', 'band49']
        self.ctx.bxsf_finished = []

    def run_wan2skeaf(self):
        """Run the `Wan2skeafCalculation`."""
        inputs = AttributeDict(
            self.exposed_inputs(Wan2skeafCalculation, namespace="wan2skeaf")
        )

        inputs.bxsf = self.inputs.bxsf
        inputs.metadata.call_link_label = "wan2skeaf"

        inputs = prepare_process_inputs(Wan2skeafCalculation, inputs)
        running = self.submit(Wan2skeafCalculation, **inputs)
        self.report(f"launching {running.process_label}<{running.pk}>")

        return ToContext(calc_wan2skeaf=running)

    def inspect_wan2skeaf(self):  # pylint: disable=inconsistent-return-statements
        """Verify that the `Wan2skeafCalculation` successfully finished."""
        calc = self.ctx.calc_wan2skeaf

        if not calc.is_finished_ok:
            self.report(
                f"{calc.process_label} failed with exit status {calc.exit_status}"
            )
            return (
                self.exit_codes.ERROR_SUB_PROCESS_FAILED_WAN2SKEAF  # pylint: disable=no-member
            )

        self.ctx.bxsf_to_run = dict(calc.outputs.output_bxsf)

    def should_run_skeaf(self) -> bool:
        """Run ``SkeafCalculation`` until ``self.ctx.bxsf_to_run`` is empty."""
        return len(self.ctx.bxsf_to_run) > 0

    def run_skeaf(self):  # pylint: disable=inconsistent-return-statements
        """Run the `SkeafCalculation` for each bxsf ``RemoteData``."""
        inputs = AttributeDict(self.exposed_inputs(SkeafCalculation, namespace="skeaf"))

        parameters = inputs.parameters.get_dict()
        w2s_output_params = self.ctx.calc_wan2skeaf.outputs[
            "output_parameters"
        ].get_dict()
        if "fermi_energy" not in parameters:
            parameters["fermi_energy"] = w2s_output_params["fermi_energy_computed"]
            inputs.parameters = orm.Dict(dict=parameters)

        # Find the min band index
        band_idx = min(self.ctx.bxsf_to_run)
        bxsf = self.ctx.bxsf_to_run.pop(band_idx)

        # Only calculate bands acrossing Fermi
        fermi_energy = parameters["fermi_energy"]
        idx = int(band_idx.removeprefix("band"))
        idx = w2s_output_params["band_indexes_in_bxsf"].index(idx)
        band_min = w2s_output_params["band_min"][idx]
        band_max = w2s_output_params["band_max"][idx]
        if band_min > fermi_energy or band_max < fermi_energy:
            return

        inputs.bxsf = bxsf
        inputs.metadata.call_link_label = f"skeaf_{band_idx}"

        inputs = prepare_process_inputs(SkeafCalculation, inputs)
        running = self.submit(SkeafCalculation, **inputs)
        self.report(f"launching {running.process_label}<{running.pk}> for {band_idx}")

        self.ctx.bxsf_finished.append(band_idx)
        return ToContext(calc_skeaf=append_(running))

    def inspect_skeaf(self):  # pylint: disable=inconsistent-return-statements
        """Verify that the `SkeafCalculation` successfully finished."""
        calc = self.ctx.calc_skeaf[-1]

        if not calc.is_finished_ok:
            self.report(
                f"{calc.process_label} failed with exit status {calc.exit_status}"
            )
            return (
                self.exit_codes.ERROR_SUB_PROCESS_FAILED_SKEAF  # pylint: disable=no-member
            )

    def results(self):
        """Attach the relevant output nodes."""

        self.out_many(
            self.exposed_outputs(
                self.ctx.calc_wan2skeaf,
                Wan2skeafCalculation,
                namespace="wan2skeaf",
            )
        )

        # essentially a dot `.`
        namespace_separator = self.spec().namespace_separator

        for i, band in enumerate(self.ctx.bxsf_finished):
            calc = self.ctx.calc_skeaf[i]
            outputs = calc.outputs._construct_attribute_dict(  # pylint: disable=protected-access
                incoming=False
            )
            self.out(f"skeaf{namespace_separator}{band}", outputs)
