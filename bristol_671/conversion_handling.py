from dataclasses import dataclass
from math import log10
from typing import TYPE_CHECKING, Any, Optional, TypeAlias

from pint import UnitRegistry

from .error_codes import SCPIErrors
from .exceptions import BristolParseError
from .selection_enums import MeasureData, PowerUnit

if TYPE_CHECKING:
    from pint import Quantity, Unit

    UnitLike: TypeAlias = str | Unit | Quantity
else:
    UnitLike: TypeAlias = str | Any

ureg: Any = UnitRegistry()


@dataclass
class Environment:
    """
    Dataclass with data return from FETCH/READ/MEASURE:ENV?
    """

    temperature: float
    pressure: float


@dataclass
class WavemeterData:
    """
    Dataclass with data returned from FETCH/READ/MEASURE:ALL?
    """

    scan_index: int
    instrument_status: int
    wavelength: float
    power: float


def dBm_to_mW(dBm: float) -> float:
    """
    Function converting dBm to mW

    Args:
        dBm (float): power in dBm

    Returns:
        float: power in mW
    """
    return 10 ** (dBm / 10)


def mW_to_dBm(mW: float) -> float:
    """
    Function converting mW to dBm

    Args:
        mW (float): power in mW

    Returns:
        float: power in dBm
    """
    return 10 * log10(mW / 1)


# to_float and to_int could be handled inside the class methods, but are added here for
# convenience, and simplifying addition of possible error handling.


def to_float(val: str) -> float:
    """
    Function converting str to float

    Args:
        val (str): string to convert to float

    Returns:
        float: converted value
    """
    return float(val)


def to_int(val: str) -> int:
    """
    Function converting str to int

    Args:
        val (str): string to convert to int

    Returns:
        int: converted value
    """
    return int(val)


def validate_response(value: str, expected_parts: int, context: str) -> list[str]:
    """
    Validate and split a comma-separated instrument response.

    Args:
        value (str): raw instrument response
        expected_parts (int): expected number of comma-separated parts
        context (str): context label included in error messages

    Returns:
        list[str]: stripped response parts
    """
    parts = [item.strip() for item in value.split(",")]
    if len(parts) != expected_parts:
        raise BristolParseError(
            f"Invalid {context} response format: {value!r}; expected "
            f"{expected_parts} comma-separated values"
        )
    return parts


def convert_environment_to_environment_data(val: str) -> Environment:
    """
    Convert return string of FETCH/READ/MEASURE:ENV? to an Environment dataclass. String
    has format "{temperature} C, {pressure} MMHG".

    Args:
        val (str): return of FETCH/READ/MEASURE:ENV?

    Returns:
        Environment: dataclass containing temperature and pressure
    """
    try:
        parts = validate_response(val, expected_parts=2, context="ENVIRONMENT")
        temperature_part, pressure_part = parts
        temperature = float(temperature_part.split()[0])
        pressure = float(pressure_part.split()[0])
        return Environment(temperature=temperature, pressure=pressure)
    except (IndexError, ValueError, BristolParseError) as exc:
        raise BristolParseError(
            f"Invalid environment response format: {val!r}"
        ) from exc


def convert_all_to_bristol_data(val: str) -> WavemeterData:
    """
    Convert return string of FETCH/READ/MEASURE:ALL? to a BristolData dataclass. String
    has format "{scan index}, {instrument status}, {wavelength}, {power}"

    Args:
        val (str): _description_

    Returns:
        BristolData: _description_
    """
    try:
        values = validate_response(val, expected_parts=4, context="ALL")

        return WavemeterData(
            scan_index=int(values[0]),
            instrument_status=int(values[1]),
            wavelength=float(values[2]),
            power=float(values[3]),
        )
    except (IndexError, ValueError, BristolParseError) as exc:
        raise BristolParseError(f"Invalid ALL response format: {val!r}") from exc


def convert_system_error(val: str) -> SCPIErrors:
    """
    Convert return string of SYSTEM:ERROR? into a SCPIErrors enum to indicate the error
    state. String has format "{error number}, {error description}".

    Args:
        val (str): retrieved error from SYSTEM:ERROR? queue

    Returns:
        SCPIErrors: enum describing the SCPI error
    """
    try:
        error_number = int(val.split(",", 1)[0].strip())
        return SCPIErrors(error_number)
    except (ValueError, TypeError) as exc:
        raise BristolParseError(f"Invalid SYSTEM:ERROR response: {val!r}") from exc


def parse_system_error(val: str) -> tuple[int, str]:
    """
    Parse return string of SYSTEM:ERROR? into error code and error message.
    String has format "{error number}, {error description}".

    Args:
        val (str): retrieved error from SYSTEM:ERROR? queue

    Returns:
        tuple[int, str]: (error code, error description)
    """
    error_code, separator, message = val.partition(",")
    if not separator:
        raise BristolParseError(
            f"Invalid SYSTEM:ERROR response format (missing comma): {val!r}"
        )

    try:
        code = int(error_code.strip())
    except ValueError as exc:
        raise BristolParseError(
            f"Invalid SYSTEM:ERROR code in response: {val!r}"
        ) from exc

    return code, message.strip().strip('"')


def convert_average_state(val: str) -> bool:
    """
    Convenience function to convert the string returned from SENSE:AVERAGE:STATE? into a
    boolean value. String is either "ON" or "OFF"

    Args:
        val (str): return of SENSE:AVERAGE:STATE?

    Raises:
        ValueError: Raise error if val is not "ON" or "OFF"

    Returns:
        bool: STATE boolean; True = ON, False = Off
    """
    if val == "ON":
        return True
    elif val == "OFF":
        return False
    else:
        raise ValueError("State not 'On' or 'Off' but '{val}'")


def convert_to_unit(
    value,
    data: MeasureData,
    unit: Optional[UnitLike],
    power_unit: Optional[PowerUnit] = None,
):
    if data == MeasureData.POWER:
        if power_unit is None:
            raise ValueError("power_unit must be provided when converting power data")
        if power_unit == PowerUnit.dBm:
            value = dBm_to_mW(value)
        return (value * ureg.milliwatt).to(unit)
    elif data == MeasureData.FREQUENCY:
        return (value * ureg.terahertz).to(unit)
    elif data == MeasureData.WAVELENGTH:
        return (value * ureg.nanometer).to(unit)
    elif data == MeasureData.WAVENUMBER:
        return (value / ureg.centimeter).to(unit)
    raise ValueError(f"Unit conversion is not supported for data type: {data.name}")
