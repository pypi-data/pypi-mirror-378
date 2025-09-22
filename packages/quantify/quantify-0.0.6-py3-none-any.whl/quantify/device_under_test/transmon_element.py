# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""The module contains definitions related to transmon elements."""

from __future__ import annotations

import math
from operator import itemgetter
from typing import TYPE_CHECKING, Any

import numpy as np
from qcodes.instrument import InstrumentChannel
from qcodes.instrument.parameter import (
    ManualParameter,
    Parameter,
)
from qcodes.utils import validators

from quantify.backends.graph_compilation import (
    DeviceCompilationConfig,
    OperationCompilationConfig,
)
from quantify.device_under_test.device_element import DeviceElement
from quantify.helpers.validators import Numbers, _Hashable
from quantify.operations import (
    composite_factories,
    measurement_factories,
    pulse_factories,
    pulse_library,
)

if TYPE_CHECKING:
    from qcodes.instrument.base import InstrumentBase


class Ports(InstrumentChannel):
    """Submodule containing the ports."""

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)

        self.microwave = Parameter(
            name="microwave",
            instrument=self,
            initial_cache_value=kwargs.get("microwave", f"{parent.name}:mw"),
            set_cmd=False,
        )
        """Name of the element's microwave port."""

        self.flux = Parameter(
            name="flux",
            instrument=self,
            initial_cache_value=kwargs.get("flux", f"{parent.name}:fl"),
            set_cmd=False,
        )
        """Name of the element's flux port."""

        self.readout = Parameter(
            name="readout",
            instrument=self,
            initial_cache_value=kwargs.get("readout", f"{parent.name}:res"),
            set_cmd=False,
        )
        """Name of the element's readout port."""


class ClocksFrequencies(InstrumentChannel):
    """Submodule containing the clock frequencies specifying the transitions to address."""  # noqa: E501

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)

        self.f01 = ManualParameter(
            name="f01",
            instrument=self,
            label="Qubit frequency",
            unit="Hz",
            initial_value=kwargs.get("f01", math.nan),
            vals=Numbers(min_value=0, max_value=1e12, allow_nan=True),
        )
        """Frequency of the 01 clock"""

        self.f12 = ManualParameter(
            name="f12",
            instrument=self,
            label="Frequency of the |1>-|2> transition",
            unit="Hz",
            initial_value=kwargs.get("f12", math.nan),
            vals=Numbers(min_value=0, max_value=1e12, allow_nan=True),
        )
        """Frequency of the 12 clock"""

        self.readout = ManualParameter(
            name="readout",
            instrument=self,
            label="Readout frequency",
            unit="Hz",
            initial_value=kwargs.get("readout", math.nan),
            vals=Numbers(min_value=0, max_value=1e12, allow_nan=True),
        )
        """Frequency of the ro clock. """


class IdlingReset(InstrumentChannel):
    """Submodule containing parameters for doing a reset by idling."""

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)

        self.duration = ManualParameter(
            name="duration",
            instrument=self,
            initial_value=kwargs.get("duration", 200e-6),
            unit="s",
            vals=validators.Numbers(min_value=0, max_value=1),
        )
        """Duration of the passive qubit reset (initialization by relaxation)."""


class RxyDRAG(InstrumentChannel):
    """
    Submodule containing parameters for performing an Rxy operation.

    The Rxy operation uses a DRAG pulse.
    """

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)
        self.amp180 = ManualParameter(
            name="amp180",
            instrument=self,
            label=r"$\pi-pulse amplitude$",
            initial_value=kwargs.get("amp180", math.nan),
            unit="",
            vals=Numbers(min_value=-10, max_value=10, allow_nan=True),
        )
        r"""Amplitude required to perform a $\pi$ pulse."""

        self.motzoi = ManualParameter(
            name="motzoi",
            instrument=self,
            initial_value=kwargs.get("motzoi", 0),
            unit="",
            vals=validators.Numbers(min_value=-1, max_value=1),
        )
        """Ratio between the Gaussian Derivative (D) and Gaussian (G)
        components of the DRAG pulse."""

        self.duration = ManualParameter(
            name="duration",
            instrument=self,
            initial_value=kwargs.get("duration", 20e-9),
            unit="s",
            vals=validators.Numbers(min_value=0, max_value=1),
        )
        """Duration of the control pulse."""

        self.add_submodule(
            name="reference_magnitude",
            submodule=ReferenceMagnitude(
                parent=self,
                name="reference_magnitude",
                dBm=kwargs.get("reference_magnitude_dBm", math.nan),
                V=kwargs.get("reference_magnitude_V", math.nan),
                A=kwargs.get("reference_magnitude_A", math.nan),
            ),
        )


class PulseCompensationModule(InstrumentChannel):
    """Submodule containing parameters for performing a PulseCompensation operation."""

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)
        self.max_compensation_amp = ManualParameter(
            name="max_compensation_amp",
            instrument=self,
            initial_value=kwargs.get("max_compensation_amp", math.nan),
            unit="",
            vals=Numbers(min_value=0, allow_nan=True),
        )
        r"""Maximum amplitude for the pulse compensation."""

        self.time_grid = ManualParameter(
            name="time_grid",
            instrument=self,
            initial_value=kwargs.get("time_grid", math.nan),
            unit="",
            vals=Numbers(min_value=0, allow_nan=True),
        )
        r"""Time grid for the duration of the compensating pulse."""

        self.sampling_rate = ManualParameter(
            name="sampling_rate",
            instrument=self,
            initial_value=kwargs.get("sampling_rate", math.nan),
            unit="",
            vals=Numbers(min_value=0, allow_nan=True),
        )
        r"""Sampling rate of the pulses."""


class DispersiveMeasurement(InstrumentChannel):
    """
    Submodule containing parameters to perform a measurement.

    The measurement that is performed is using
    :func:`~quantify.operations.measurement_factories.dispersive_measurement_transmon`.
    """

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)

        pulse_types = validators.Enum("SquarePulse")
        self.pulse_type = ManualParameter(
            name="pulse_type",
            instrument=self,
            initial_value=kwargs.get("pulse_type", "SquarePulse"),
            vals=pulse_types,
        )
        """Envelope function that defines the shape of the readout pulse prior to
        modulation."""

        self.pulse_amp = ManualParameter(
            name="pulse_amp",
            instrument=self,
            initial_value=kwargs.get("pulse_amp", 0.25),
            unit="",
            vals=validators.Numbers(min_value=0, max_value=1),
        )
        """Amplitude of the readout pulse."""

        self.pulse_duration = ManualParameter(
            name="pulse_duration",
            instrument=self,
            initial_value=kwargs.get("pulse_duration", 300e-9),
            unit="s",
            vals=validators.Numbers(min_value=0, max_value=1),
        )
        """Duration of the readout pulse."""

        self.acq_channel = ManualParameter(
            name="acq_channel",
            instrument=self,
            initial_value=kwargs.get("acq_channel", 0),
            unit="",
            vals=_Hashable(),
        )
        """Acquisition channel of to this device element."""

        self.acq_delay = ManualParameter(
            name="acq_delay",
            instrument=self,
            initial_value=kwargs.get("acq_delay", 0),
            unit="s",
            # in principle the values should be a few 100 ns but the validator is here
            # only to protect against silly typos that lead to out of memory errors.
            vals=validators.Numbers(min_value=0, max_value=100e-6),
        )
        """Delay between the start of the readout pulse and the start of
        the acquisition. Note that some hardware backends do not support
        starting a pulse and the acquisition in the same clock cycle making 0
        delay an invalid value."""

        self.integration_time = ManualParameter(
            name="integration_time",
            instrument=self,
            initial_value=kwargs.get("integration_time", 1e-6),
            unit="s",
            # in principle the values should be a few us but the validator is here
            # only to protect against silly typos that lead to out of memory errors.
            vals=validators.Numbers(min_value=0, max_value=100e-6),
        )
        """Integration time for the readout acquisition."""

        self.reset_clock_phase = ManualParameter(
            name="reset_clock_phase",
            instrument=self,
            initial_value=kwargs.get("reset_clock_phase", True),
            vals=validators.Bool(),
        )
        """The phase of the measurement clock will be reset by the
        control hardware at the start of each measurement if
        ``reset_clock_phase=True``."""

        self.acq_weights_a = ManualParameter(
            name="acq_weights_a",
            instrument=self,
            initial_value=kwargs.get("acq_weights_a", np.array([], dtype=np.float64)),
            vals=validators.Arrays(),
        )
        """The weights for the I path. Used when specifying the
        ``"NumericalSeparatedWeightedIntegration"`` or the
        ``"NumericalWeightedIntegration"`` acquisition protocol."""

        self.acq_weights_b = ManualParameter(
            name="acq_weights_b",
            instrument=self,
            initial_value=kwargs.get("acq_weights_b", np.array([], dtype=np.float64)),
            vals=validators.Arrays(),
        )
        """The weights for the Q path. Used when specifying the
        ``"NumericalSeparatedWeightedIntegration"`` or the
        ``"NumericalWeightedIntegration"`` acquisition protocol."""

        self.acq_weights_sampling_rate = ManualParameter(
            name="acq_weights_sampling_rate",
            instrument=self,
            initial_value=kwargs.get("acq_weights_sampling_rate"),
            vals=validators.Numbers(min_value=1, max_value=10e9),
        )
        """The sample rate of the weights arrays, in Hertz. Used when specifying the
        ``"NumericalSeparatedWeightedIntegration"`` or the
        ``"NumericalWeightedIntegration"`` acquisition protocol."""

        ro_acq_weight_type_validator = validators.Enum("SSB", "Numerical")
        self.acq_weight_type = ManualParameter(
            name="acq_weight_type",
            instrument=self,
            initial_value=kwargs.get("acq_weight_type", "SSB"),
            vals=ro_acq_weight_type_validator,
        )

        self.add_submodule(
            name="reference_magnitude",
            submodule=ReferenceMagnitude(
                parent=self,
                name="reference_magnitude",
                dBm=kwargs.get("reference_magnitude_dBm", math.nan),
                V=kwargs.get("reference_magnitude_V", math.nan),
                A=kwargs.get("reference_magnitude_A", math.nan),
            ),
        )

        self.acq_rotation = ManualParameter(
            "acq_rotation",
            instrument=self,
            initial_value=kwargs.get("acq_rotation", 0),
        )
        """The phase rotation in degrees required to perform thresholded
        acquisition. Note that rotation is performed before the threshold. For
        more details see
        :class:`~quantify.operations.acquisition_library.ThresholdedAcquisition`."""  # noqa

        self.acq_threshold = ManualParameter(
            "acq_threshold",
            instrument=self,
            initial_value=kwargs.get("acq_threshold", 0),
        )
        """The threshold value against which the rotated and integrated result
        is compared against. For more details see
        :class:`~quantify.operations.acquisition_library.ThresholdedAcquisition`."""  # noqa

        self.num_points = ManualParameter(
            name="num_points",
            instrument=self,
            initial_value=kwargs.get("num_points"),
            vals=validators.Ints(min_value=1),
        )
        """
        Number of data points to be acquired during the measurement.

        This parameter defines how many discrete data points will be collected
        in the course of a single measurement sequence. """


class ReferenceMagnitude(InstrumentChannel):
    """
    Submodule which describes an amplitude / power reference level.

    The reference level is with respect to which pulse amplitudes are defined.
    This can be specified in units of "V", "dBm" or "A".

    Only one unit parameter may have a defined value at a time. If we call the
    set method for any given unit parameter, all other unit parameters will be
    automatically set to nan.
    """

    def __init__(  # noqa: D107
        self,
        parent: InstrumentBase,
        name: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(parent=parent, name=name)

        self.dBm = Parameter(
            "reference_magnitude_dBm",
            instrument=self,
            initial_value=kwargs.get("dBm", math.nan),
            set_cmd=lambda value: self._set_parameter(value, "reference_magnitude_dBm"),
            unit="dBm",
            vals=Numbers(allow_nan=True),
        )
        self.V = Parameter(
            "reference_magnitude_V",
            instrument=self,
            initial_value=kwargs.get("V", math.nan),
            set_cmd=lambda value: self._set_parameter(value, "reference_magnitude_V"),
            unit="V",
            vals=Numbers(allow_nan=True),
        )
        self.A = Parameter(
            "reference_magnitude_A",
            instrument=self,
            initial_value=kwargs.get("A", math.nan),
            set_cmd=lambda value: self._set_parameter(value, "reference_magnitude_A"),
            unit="A",
            vals=Numbers(allow_nan=True),
        )

    def _set_parameter(self, value: float, parameter: str) -> None:
        """
        Set the value of one of the unit parameters.

        All the other unit parameters are set to nan.
        """
        for name, par in self.parameters.items():
            if name == parameter:
                par.cache.set(value)
            elif not math.isnan(value):
                par.cache.set(math.nan)

    def get_val_unit(self) -> tuple[float, str]:
        """
        Get the value of the amplitude reference and its unit, if one is defined.

        If a value is defined for more than one unit, raise an exception.

        Returns
        -------
        value
            The value of the amplitude reference
        unit
            The unit in which this value is specified

        """
        value_and_unit = math.nan, ""
        for param in self.parameters.values():
            if not math.isnan(value := param()):
                if math.isnan(value_and_unit[0]):
                    value_and_unit = value, param.unit  # type: ignore
                else:
                    raise ValueError(
                        "ReferenceMagnitude values defined for multiple units. Only "
                        "one unit may be defined at a time."
                    )
        return value_and_unit


class BasicTransmonElement(DeviceElement):
    """
    A device element representing a single fixed-frequency transmon qubit.

    The qubit is coupled to a readout resonator.

    Parameters
    ----------
    name
        The name of the transmon element.
    kwargs
        Can be used to pass submodule initialization data by using submodule name
        as keyword and as argument a dictionary containing the submodule parameter
        names and their value.

    """

    _ELEMENT_TEMPLATE: dict[str, dict[str, Any]] = {
        "reset": {
            "factory": pulse_library.IdlePulse,
            "kwargs": {
                "duration": itemgetter("reset_dur"),
            },
        },
        "Rxy": {
            "factory": pulse_factories.rxy_drag_pulse,
            "kwargs": {
                "amp180": itemgetter("rxy_amp180"),
                "motzoi": itemgetter("rxy_motzoi"),
                "port": itemgetter("mic_port"),
                "clock": itemgetter("clk_01"),
                "duration": itemgetter("rxy_dur"),
                "reference_magnitude": itemgetter("rxy_refmag"),
            },
            "gate_keys": ["theta", "phi"],
        },
        "Rz": {
            "factory": pulse_factories.phase_shift,
            "kwargs": {
                "clock": itemgetter("clk_01"),
            },
            "gate_keys": ["theta"],
        },
        "H": {
            "factory": composite_factories.hadamard_as_y90z,
            "kwargs": {
                "qubit": itemgetter("name"),
            },
        },
        "pulse_compensation": {
            "factory": None,
            "kwargs": {
                "port": itemgetter("mic_port"),
                "clock": itemgetter("clk_01"),
                "max_compensation_amp": itemgetter("pulse_comp_max_amp"),
                "time_grid": itemgetter("pulse_comp_time_grid"),
                "sampling_rate": itemgetter("pulse_comp_sampling_rate"),
            },
        },
        "measure": {
            "factory": measurement_factories._dispersive_measurement,
            "kwargs": {
                "port": itemgetter("ro_port"),
                "clock": itemgetter("clk_ro"),
                "pulse_type": itemgetter("meas_pulse_type"),
                "pulse_amp": itemgetter("meas_pulse_amp"),
                "pulse_duration": itemgetter("meas_pulse_dur"),
                "acq_delay": itemgetter("meas_acq_delay"),
                "acq_duration": itemgetter("meas_acq_dur"),
                "acq_channel": itemgetter("meas_acq_chan"),
                "acq_protocol_default": "SSBIntegrationComplex",
                "reset_clock_phase": itemgetter("meas_reset_clk"),
                "reference_magnitude": itemgetter("meas_refmag"),
                "acq_weights_a": itemgetter("meas_wt_a"),
                "acq_weights_b": itemgetter("meas_wt_b"),
                "acq_weights_sampling_rate": itemgetter("meas_wt_rate"),
                "acq_rotation": itemgetter("meas_rotation"),
                "acq_threshold": itemgetter("meas_threshold"),
                "num_points": itemgetter("meas_num_points"),
                "freq": None,
                "gate_pulse_amp": None,
                "gate_port": None,
            },
            "gate_keys": [
                "acq_channel_override",
                "acq_index",
                "bin_mode",
                "acq_protocol",
                "feedback_trigger_label",
            ],
        },
    }

    def __init__(self, name: str, **kwargs) -> None:  # noqa: D107
        submodules_to_add = {
            "reset": IdlingReset,
            "rxy": RxyDRAG,
            "measure": DispersiveMeasurement,
            "pulse_compensation": PulseCompensationModule,
            "ports": Ports,
            "clock_freqs": ClocksFrequencies,
        }
        submodule_data = {
            sub_name: kwargs.pop(sub_name, {}) for sub_name in submodules_to_add
        }
        super().__init__(name, **kwargs)

        for sub_name, sub_class in submodules_to_add.items():
            self.add_submodule(
                sub_name,
                sub_class(
                    parent=self, name=sub_name, **submodule_data.get(sub_name, {})
                ),
            )

        self.reset: IdlingReset
        """Submodule :class:`~.IdlingReset`."""
        self.rxy: RxyDRAG
        """Submodule :class:`~.RxyDRAG`."""
        self.measure: DispersiveMeasurement
        """Submodule :class:`~.DispersiveMeasurement`."""
        self.pulse_compensation: PulseCompensationModule
        """Submodule :class:`~.PulseCompensationModule`."""
        self.ports: Ports
        """Submodule :class:`~.Ports`."""
        self.clock_freqs: ClocksFrequencies
        """Submodule :class:`~.ClocksFrequencies`."""

    @classmethod
    def get_element_template(cls) -> dict:
        """
        Returns the merged static operation template for this transmon element.

        See `DeviceElement.get_element_template` for extension and override pattern.
        """
        return super().get_element_template()

    @property
    def pre_computed_calls(self) -> dict:
        """
        Runtime values for this transmon element.

        See `DeviceElement.pre_computed_calls` for extension and override pattern.
        """
        return {
            "reset_dur": self.reset.duration(),
            "rxy_dur": self.rxy.duration(),
            "rxy_refmag": pulse_library.ReferenceMagnitude.from_parameter(  # noqa: E501
                self.rxy.reference_magnitude
            ),
            "rxy_amp180": self.rxy.amp180(),
            "rxy_motzoi": self.rxy.motzoi(),
            "mic_port": self.ports.microwave(),
            "clk_01": f"{self.name}.01",
            "name": self.name,
            "pulse_comp_max_amp": self.pulse_compensation.max_compensation_amp(),
            "pulse_comp_time_grid": self.pulse_compensation.time_grid(),
            "pulse_comp_sampling_rate": self.pulse_compensation.sampling_rate(),
            "ro_port": self.ports.readout(),
            "clk_ro": f"{self.name}.ro",
            "meas_pulse_type": self.measure.pulse_type(),
            "meas_pulse_amp": self.measure.pulse_amp(),
            "meas_pulse_dur": self.measure.pulse_duration(),
            "meas_acq_delay": self.measure.acq_delay(),
            "meas_acq_dur": self.measure.integration_time(),
            "meas_acq_chan": self.measure.acq_channel(),
            "meas_reset_clk": self.measure.reset_clock_phase(),
            "meas_refmag": pulse_library.ReferenceMagnitude.from_parameter(  # noqa: E501
                self.measure.reference_magnitude
            ),
            "meas_wt_a": self.measure.acq_weights_a(),
            "meas_wt_b": self.measure.acq_weights_b(),
            "meas_wt_rate": self.measure.acq_weights_sampling_rate(),
            "meas_rotation": self.measure.acq_rotation(),
            "meas_threshold": self.measure.acq_threshold(),
            "meas_num_points": self.measure.num_points(),
        }

    def _generate_config(self) -> dict[str, dict[str, OperationCompilationConfig]]:
        """
        Generate part of the device configuration specific to a single qubit.

        This method is intended to be used when this object is part of a
        device object containing multiple elements.
        """
        return super()._generate_config()

    def generate_device_config(self) -> DeviceCompilationConfig:
        """
        Generate a valid device config.

        The config will be used for the quantify-scheduler making use of the
        :func:`~.circuit_to_device.compile_circuit_to_device_with_config_validation`
        function.

        This enables the settings of this device element to be used in isolation.

        .. note:

            This config is only valid for single qubit experiments.
        """
        cfg_dict = {
            "elements": self._generate_config(),
            "clocks": {
                f"{self.name}.01": self.clock_freqs.f01(),
                f"{self.name}.12": self.clock_freqs.f12(),
                f"{self.name}.ro": self.clock_freqs.readout(),
            },
            "edges": {},
        }
        dev_cfg = DeviceCompilationConfig.model_validate(cfg_dict)

        return dev_cfg
