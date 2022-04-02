from dataclasses import dataclass

from math import log10

from astropy import units
from astropy.units import cds

from .error_codes import SCPIErrors
from .selection_enums import MeasureData, PowerUnit


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


def convert_environment_to_environment_data(val: str) -> Environment:
    """
    Convert return string of FETCH/READ/MEASURE:ENV? to an Environment dataclass. String
    has format "{temperature} C, {pressure} MMHG".

    Args:
        val (str): return of FETCH/READ/MEASURE:ENV?

    Returns:
        Environment: dataclass containing temperature and pressure
    """
    values = val.split(",")
    values[0] = float(values[0].strip("C"))
    values[1] = float(values[1].strip("MMHG"))
    return Environment(*values)


def convert_all_to_bristol_data(val: str) -> WavemeterData:
    """
    Convert return string of FETCH/READ/MEASURE:ALL? to a BristolData dataclass. String
    has format "{scan index}, {instrument status}, {wavelength}, {power}"

    Args:
        val (str): _description_

    Returns:
        BristolData: _description_
    """
    values = val.split(",")
    values = [t(val) for t, val in zip((int, int, float, float), values)]
    return WavemeterData(*values)


def convert_sytem_error(val: str) -> SCPIErrors:
    """
    Convert return string of SYSTEM:ERROR? into a SCPIErrors enum to indicate the error
    state. String has format "{error number}, {error description}".

    Args:
        val (str): retrieved error from SYSTEM:ERROR? queue

    Returns:
        SCPIErrors: enum describing the SCPI error
    """
    return SCPIErrors(int(val.split(",")))


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


def convert_to_unit(value, data: MeasureData, power_unit: PowerUnit, unit=None):
    if data == MeasureData.POWER:
        if power_unit == PowerUnit.dBm:
            value = dBm_to_mW(value)
        return (value * units.mW).to(unit)
    elif data == MeasureData.FREQUENCY:
        return (value * units.THz).to(unit)
    elif data == MeasureData.WAVELENGTH:
        return (value * units.nm).to(unit)
    elif data == MeasureData.WAVENUMBER:
        return (value * (1 / units.cm)).to(unit)
    elif data == MeasureData.ENVIRONMENT:
        value[0] = value[0] * units.C
        value[1] = value[1] * cds.mmHg.to(units.Pa)
        return tuple(value)
