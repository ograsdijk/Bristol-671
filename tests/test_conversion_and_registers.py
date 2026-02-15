import pytest

from bristol_671.conversion_handling import (
    convert_all_to_bristol_data,
    convert_environment_to_environment_data,
    convert_system_error,
    convert_to_unit,
    parse_system_error,
)
from bristol_671.error_codes import SCPIErrors
from bristol_671.exceptions import BristolParseError
from bristol_671.registers import EventStatusRegister
from bristol_671.selection_enums import MeasureData


def test_convert_system_error_parses_code():
    err = convert_system_error('-101, "Invalid character"')

    assert err == SCPIErrors.INVALID_CHARACTER


def test_parse_system_error_parses_message():
    code, message = parse_system_error('-230, "Data corrupt or stale"')

    assert code == -230
    assert message == "Data corrupt or stale"


def test_parse_system_error_parses_whitespace_and_quotes():
    code, message = parse_system_error(' -101 ,   "Invalid character"  ')

    assert code == -101
    assert message == "Invalid character"


def test_convert_to_unit_requires_power_unit_for_power():
    with pytest.raises(ValueError, match="power_unit"):
        convert_to_unit(10.0, MeasureData.POWER, unit=None)


def test_convert_to_unit_uses_pint_unit_strings():
    value = convert_to_unit(1.0, MeasureData.FREQUENCY, unit="gigahertz")

    assert value.magnitude == pytest.approx(1000.0)
    assert str(value.units) == "gigahertz"


def test_convert_environment_rejects_malformed_data():
    with pytest.raises(BristolParseError):
        convert_environment_to_environment_data("bad_data")


def test_convert_environment_accepts_whitespace_variants():
    env = convert_environment_to_environment_data(" 25.4 C ,  755.2 MMHG ")

    assert env.temperature == pytest.approx(25.4)
    assert env.pressure == pytest.approx(755.2)


def test_convert_all_rejects_malformed_data():
    with pytest.raises(BristolParseError):
        convert_all_to_bristol_data("1,2,3")


def test_parse_system_error_rejects_missing_comma():
    with pytest.raises(BristolParseError):
        parse_system_error("-101 Invalid character")


def test_register_is_ok_true_without_faults():
    register = EventStatusRegister(0)

    assert register.is_ok is True


def test_register_is_ok_false_with_fault():
    # Bit 5 corresponds to COMMAND_ERROR
    register = EventStatusRegister(1 << 5)

    assert register.is_ok is False
