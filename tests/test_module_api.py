from types import SimpleNamespace
from typing import Any

import pytest

import bristol_671.module as module_lib
from bristol_671.error_codes import SCPIErrors
from bristol_671.exceptions import SCPICommandError
from bristol_671.module import Bristol671
from bristol_671.selection_enums import MeasureData, MeasureMethod, PowerUnit


def _make_uninitialized_meter() -> Bristol671:
    # Avoid inherited easy_scpi destructor side effects on partially-initialized
    # instances created via __new__ in tests.
    Bristol671.__del__ = lambda self: None
    return Bristol671.__new__(Bristol671)


def test_pythonic_command_methods_write_expected_scpi(monkeypatch):
    meter = _make_uninitialized_meter()
    sent = []

    monkeypatch.setattr(meter, "write", sent.append)

    meter.clear_status()
    meter.restore_state()
    meter.reset()
    meter.save_state()

    assert sent == ["*CLS", "*RCL", "*RST", "*SAV"]


def test_uppercase_command_methods_write_expected_scpi(monkeypatch):
    meter = _make_uninitialized_meter()
    sent = []

    monkeypatch.setattr(meter, "write", sent.append)

    meter.CLS()
    meter.RCL()
    meter.RST()
    meter.SAV()

    assert sent == ["*CLS", "*RCL", "*RST", "*SAV"]


def test_get_data_executes_selected_method():
    meter = _make_uninitialized_meter()

    meter.read_frequency = lambda: 193.1

    value = meter.get_data(MeasureData.FREQUENCY, MeasureMethod.READ)

    assert value == 193.1


def test_get_data_converts_power_units(monkeypatch):
    meter = _make_uninitialized_meter()
    sentinel = object()

    meter.read_power = lambda: 10.0
    monkeypatch.setattr(
        Bristol671,
        "unit_power",
        property(lambda self: PowerUnit.mW),
    )
    monkeypatch.setattr(
        module_lib,
        "convert_to_unit",
        lambda value, data, unit=None, power_unit=None: (
            sentinel,
            value,
            data,
            unit,
            power_unit,
        ),
    )

    marker_unit: Any = object()
    value = meter.get_data(MeasureData.POWER, MeasureMethod.READ, unit=marker_unit)

    assert value == (sentinel, 10.0, MeasureData.POWER, marker_unit, PowerUnit.mW)


def test_system_error_properties_parse_error_queue():
    meter = _make_uninitialized_meter()
    setattr(meter, "system", SimpleNamespace(error=lambda: '-101, "Invalid character"'))

    assert meter.system_error.name == "INVALID_CHARACTER"
    assert meter.system_error_message == "Invalid character"


def test_average_count_requires_positive_int():
    meter = _make_uninitialized_meter()
    setattr(meter, "sense", SimpleNamespace(average=SimpleNamespace(count=lambda x: x)))

    with pytest.raises(SCPICommandError, match="> 0"):
        meter.average_count = 0


def test_ese_setter_requires_byte_range(monkeypatch):
    meter = _make_uninitialized_meter()
    sent = []
    monkeypatch.setattr(meter, "write", sent.append)

    with pytest.raises(SCPICommandError, match=r"\[0, 255\]"):
        meter.ESE = 256

    meter.ESE = 255
    assert sent[-1] == "*ESE 255"


def test_context_manager_calls_close_when_available():
    meter = _make_uninitialized_meter()
    state = {"closed": False}
    object.__setattr__(meter, "close", lambda: state.__setitem__("closed", True))

    with meter as active:
        assert active is meter

    assert state["closed"] is True


def test_drain_error_queue_returns_all_entries():
    meter = _make_uninitialized_meter()
    queue = iter(
        [
            '-101, "Invalid character"',
            '0, "No error"',
        ]
    )
    setattr(meter, "system", SimpleNamespace(error=lambda: next(queue)))

    drained = meter.drain_error_queue()

    assert drained == [
        (SCPIErrors.INVALID_CHARACTER, "Invalid character"),
        (SCPIErrors.NO_ERROR, "No error"),
    ]


def test_drain_error_queue_raises_when_requested():
    meter = _make_uninitialized_meter()
    queue = iter(
        [
            '-101, "Invalid character"',
            '0, "No error"',
        ]
    )
    setattr(meter, "system", SimpleNamespace(error=lambda: next(queue)))

    with pytest.raises(SCPICommandError, match="active errors"):
        meter.drain_error_queue(raise_on_error=True)
