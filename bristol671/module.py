from typing import Optional, Tuple

import easy_scpi as scpi
from astropy.units.core import NamedUnit

from .conversion_handling import (
    Environment,
    WavemeterData,
    convert_all_to_bristol_data,
    convert_average_state,
    convert_environment_to_environment_data,
    convert_sytem_error,
    convert_to_unit,
    to_float,
    to_int,
)
from .error_codes import SCPIErrors
from .registers import (
    EventStatusEnableRegister,
    EventStatusRegister,
    InstrumentStatusByte,
    QuestionableStatusRegister,
)
from .selection_enums import MeasureData, MeasureMethod, PowerUnit


class Bristol671(scpi.Instrument):
    def __init__(self, port, timeout=2):
        super().__init__(
            port=port, timeout=timeout, read_termination="\n", write_termination="\n"
        )

    def __repr__(self):
        return f"Bristol671(port = {self.port})"

    def get(
        self, data: MeasureData, method: MeasureMethod, unit: Optional[NamedUnit] = None
    ) -> Tuple[float, int, WavemeterData, Environment]:
        """
        Get a `data` type measurement using method `method` with the units given by
        `unit`.

        Args:
            data (Data): data measurement type
            method (Method): data measurement method
            unit (Optional[Unit], optional): Unit to convert data to. Defaults to None.

        Returns:
            Tuple[float, int, WavemeterData, Environment]: value for the specified
            `data` type and specified `method` converted to the specified `unit`
        """
        assert isinstance(data, MeasureData)
        assert isinstance(method, MeasureMethod)
        val = getattr(self, f"{method.name.lower()}_{data.name.lower()}")
        if unit is None:
            return val
        else:
            return convert_to_unit(val, data, unit)

    @property
    def event_status_enable_register(self) -> EventStatusEnableRegister:
        """
        Get the standard event status enable register. Determines which bits in the
        standard event status register (ESR) are active.

        Returns:
            EventStatusEnableRegister: ESE register
        """
        return EventStatusEnableRegister(self.ESE)

    @property
    def event_status_register(self) -> EventStatusRegister:
        """
        Get the standard event status register.
        Register values are:
        7 : POWER ON
        5 : COMMAND ERROR (CME)
        4 : EXECUTION ERROR (EXE)
        3 : DEVICE DEPENDED ERROR (DDE)
        2 : QUERY ERROR (QYE)
        0 : OPERATION COMPLETE

        Returns:
            EventStatusRegister: ESR register
        """
        return EventStatusRegister(self.ESR)

    @property
    def status_register(self) -> InstrumentStatusByte:
        """
        Get the Instrument Status Bit.
        Register values are:
        5 : BIT SET IN QUESTIONABLE REGISTER
        3 : ERRORS IN THE ERROR QUEUE
        2 : BIT SET IN THE EVENT STATUS REGISTER

        Returns:
            InstrumentStatusByte: STB register
        """
        return InstrumentStatusByte(self.STB)

    @property
    def _questionable_condition_register(self) -> int:
        """
        Get the questionable condition register.
        Register values are:
        0 : WAVELENGTH ALREADY READ FOR THE CURRENT SCAN
        3 : POWER OUT OF RANGE
        4 : TEMPERATURE OUT OF RANGE
        5 : WAVELENGTH OUTSIDE OF RANGE
        9 : PRESSURE OUT OF RANGE
        10 : REFERENCE LASER NOT STABILIZED

        Returns:
            int: questionable status register
        """
        return to_int(self.status.questionable.condition())

    @property
    def questionable_condition_register(self) -> QuestionableStatusRegister:
        """
        Get the questionable condition register.
        Register values are:
        0 : WAVELENGTH ALREADY READ FOR THE CURRENT SCAN
        3 : POWER OUT OF RANGE
        4 : TEMPERATURE OUT OF RANGE
        5 : WAVELENGTH OUTSIDE OF RANGE
        9 : PRESSURE OUT OF RANGE
        10 : REFERENCE LASER NOT STABILIZED

        Returns:
            QuestionableStatusRegister: questionable condition register
        """
        val = self._questionable_condition_register
        return QuestionableStatusRegister(val)

    @property
    def _questionable_enable_register(self) -> int:
        """
        Get the questionable enable register. Determines which bits in the
        questionable conditon register are active.

        Returns:
            int: questionable enable register
        """
        return to_int(self.status.questionable.enable)

    @_questionable_enable_register.setter
    def _questionable_enable_register(self, value: int):
        """
        Write the questionable enable register.

        Args:
            val (int): integer value of the questionable enable register
        """
        assert isinstance(value, int)
        self.status.questionable.enable(value)

    def CLS(self) -> None:
        """
        Clear the event satus register (ESE) and error queue (SYSTEM:ERROR)
        """
        self.write("*CLS")

    @property
    def ESE(self) -> int:
        """
        Get the standard event status enable register. Determines which bits in the
        standard event status register (ESR) are active.

        Returns:
            int: ESE register
        """
        return to_int(self.query("*ESE?"))

    @ESE.setter
    def ESE(self, val: int) -> None:
        """
        Write the standard event status enable register.

        Args:
            val (int): integer value of the standard status enable register
        """
        self.write(f"*ESE {val}")

    @property
    def ESR(self) -> int:
        """
        Get the standard event status register.
        Register values are:
        7 : POWER ON
        5 : COMMAND ERROR (CME)
        4 : EXECUTION ERROR (EXE)
        3 : DEVICE DEPENDED ERROR (DDE)
        2 : QUERY ERROR (QYE)
        0 : OPERATION COMPLETE

        Returns:
            int: ESR register
        """
        return to_int(self.query("*ESR?"))

    @property
    def OPC(self) -> int:
        """
        Get value of the OPERATION COMPLETE bit in the standard event status register
        (*ESR?)

        Returns:
            int: _description_
        """
        return to_int(self.query("*OPC?"))

    def RCL(self) -> None:
        """
        Restore instrument settings from settings last saved with *SAV?.
        """
        self.write("*RCL")

    def RST(self) -> None:
        """
        Reset instrument to default settings.
        """
        self.write("*RST")

    def SAV(self) -> None:
        """
        Save instrument settings.
        """
        self.write("*SAV")

    @property
    def STB(self) -> int:
        """
        Get the Instrument Status Bit.
        Register values are:
        5 : BIT SET IN QUESTIONABLE REGISTER
        3 : ERRORS IN THE ERROR QUEUE
        2 : BIT SET IN THE EVENT STATUS REGISTER

        Returns:
            int: STB register
        """
        return to_int(self.query("*STB?"))

    # FETCH     : returns reading based on the last complete scan
    # READ      : return reading based on the current scan
    # MEASURE   : return reading based on the next scan
    # READ and MEASURE guarantee each returned reading is a new one
    # To retrieve multiple types, use a READ followed by multiple FETCH

    def fetch_environment(self) -> Environment:
        """
        FETCH:ENVIRONMENT?. Environment variables are temperature (C) and pressure
        (mmHg).

        Returns:
            Environment: dataclass with temperature (C) and pressure (mmHG)
        """
        return convert_environment_to_environment_data(self.fetch.env())

    def read_environment(self) -> Environment:
        """
        READ:ENVIRONMENT?. Environment variables are temperature (C) and pressure
        (mmHg).

        Returns:
            Environment: dataclass with temperature (C) and pressure (mmHG)
        """
        return convert_environment_to_environment_data(self.read.env())

    def measure_environment(self) -> Environment:
        """
        MEASURE:ENVIRONMENT?. Environment variables are temperature (C) and pressure
        (mmHg).

        Returns:
            Environment: dataclass with temperature (C) and pressure (mmHG)
        """
        return convert_environment_to_environment_data(self.measure.env())

    def fetch_wavelength(self) -> float:
        """
        FETCH:WAVELENGTH?. Wavelength is returned in nm

        Returns:
            float: wavelength (nm)
        """
        return to_float(self.fetch.wavelength())

    def read_wavelength(self) -> float:
        """
        READ:WAVELENGTH?. Wavelength is returned in nm

        Returns:
            float: wavelength (nm)
        """
        return to_float(self.read.wavelength())

    def measure_wavelength(self) -> float:
        """
        MEASURE:WAVELENGTH?. Wavelength is returned in nm

        Returns:
            float: wavelength (nm)
        """
        return to_float(self.measure.wavelength())

    def fetch_frequency(self) -> float:
        """
        FETCH:FREQUENCY?. Frequency is returned in THz

        Returns:
            float: frequency (THz)
        """
        return to_float(self.fetch.frequency())

    def read_frequency(self) -> float:
        """
        READ:FREQUENCY?. Frequency is returned in THz

        Returns:
            float: frequency (THz)
        """
        return to_float(self.read.frequency())

    def measure_frequency(self) -> float:
        """
        MEASURE:FREQUENCY?. Frequency is returned in THz

        Returns:
            float: frequency (THz)
        """
        return to_float(self.measure.frequency())

    def fetch_power(self) -> float:
        """
        FETCH:POWER?. Power is returned in either mW or dBm. Use `unit_power` to check.

        Returns:
            float: power (mW / dBm)
        """
        return to_float(self.fetch.power())

    def read_power(self) -> float:
        """
        READ:POWER?. Power is returned in either mW or dBm. Use `unit_power` to check.

        Returns:
            float: power (mW / dBm)
        """
        return to_float(self.read.power())

    def measure_power(self) -> float:
        """
        MEASURE:POWER?. Power is returned in either mW or dBm. Use `unit_power` to
        check.

        Returns:
            float: power (mW / dBm)
        """
        return to_float(self.measure.power())

    def fetch_wavenumber(self) -> float:
        """
        FETCH:WAVENUMBER?. Wavenumber is returned in cm^-1

        Returns:
            float: wavenumber (cm^-1)
        """
        return to_float(self.fetch.wnumber())

    def read_wavenumber(self) -> float:
        """
        READ:WAVENUMBER?. Wavenumber is returned in cm^-1

        Returns:
            float: wavenumber (cm^-1)
        """
        return to_float(self.read.wnumber())

    def measure_wavenumber(self) -> float:
        """
        MEASURE:WAVENUMBER?. Wavenumber is returned in cm^-1

        Returns:
            float: wavenumber (cm^-1)
        """
        return to_float(self.measure.wnumber())

    def fetch_all(self) -> WavemeterData:
        """
        FETCH:ALL?. ALL variables are scan index, instrument status, wavelength (nm) and
        power (mW / dBm). Power unit can be found with `unit_power`.

        Returns:
            BristolData: dataclass with scan index, instrument status, wavelength (nm)
                        and power (mW / dBm)
        """
        return convert_all_to_bristol_data(self.fetch.all())

    def read_all(self) -> WavemeterData:
        """
        READ:ALL?. ALL variables are scan index, instrument status, wavelength (nm) and
        power (mW / dBm). Power unit can be found with `unit_power`.

        Returns:
            BristolData: dataclass with scan index, instrument status, wavelength (nm)
                        and power (mW / dBm)
        """
        return convert_all_to_bristol_data(self.read.all())

    def measure_all(self) -> WavemeterData:
        """
        MEASURE:ALL?. ALL variables are scan index, instrument status, wavelength (nm)
        and power (mW / dBm). Power unit can be found with `unit_power`.

        Returns:
            BristolData: dataclass with scan index, instrument status, wavelength (nm)
                        and power (mW / dBm)
        """
        return convert_all_to_bristol_data(self.measure.all())

    @property
    def average_state(self) -> bool:
        """
        Get the state of averaging, either ON or OFF.

        Returns:
            bool: True (ON), False (OFF)
        """
        return convert_average_state(self.sense.average.state())

    @average_state.setter
    def average_state(self, state: bool):
        """
        Set averaging state, ON or OFF.

        Args:
            state (bool): True (ON), False (OFF)
        """
        assert isinstance(state, bool)
        self.sense.average.state(state)

    @property
    def average_count(self) -> int:
        """
        Get the averaging count. E.g. number of samples to average.

        Returns:
            int: averaging count
        """
        return to_int(self.sense.average.count())

    @average_count.setter
    def average_count(self, count: int):
        """
        Set the averaging count. E.g. number of samples to average.

        Args:
            count (int): number of samples to average.
        """
        assert isinstance(count, int)
        self.sense.average.count(count)

    def get_average_data(self, data: MeasureData) -> float:
        """
        Get the average value for `data` for the past n values, where n is given by
        `average_count`, where `data` is one of the enum values of average measurements
        possible on the wavelength meter.
        Valid Data enum values are:
        POWER, WAVELENGTH, FREQUENCY, WAVENUMBER

        Args:
            data (Data): enum with data measurements possible on the wavelength meter.

        Returns:
            float: average value of the data enum value
        """
        assert isinstance(data, MeasureData)
        assert data in [
            MeasureData.POWER,
            MeasureData.FREQUENCY,
            MeasureData.WAVELENGTH,
            MeasureData.WAVENUMBER,
        ]
        return self.query(f"SENSE:AVERAGE:DATA? {data.name}")

    @property
    def unit_power(self) -> PowerUnit:
        """
        Get the units of the power measurment, either mW or dBm

        Returns:
            PowerUnit: enum with either mW or dBm power units.
        """
        unit_power = self.unit.power()
        if unit_power == "DBM":
            return PowerUnit.dBm
        elif unit_power == "MW":
            return PowerUnit.mW

    @unit_power.setter
    def unit_power(self, unit: PowerUnit):
        """
        Set the units of the power measurement, either mW or dBm, using the PowerUnit
        enum.

        Args:
            unit (PowerUnit): enum with either mW or dBm
        """
        assert isinstance(unit, PowerUnit)
        self.unit.power(unit.name)

    @property
    def system_error(self) -> SCPIErrors:
        """
        SYSTEM:ERROR?. Retrieve the error from the fifo SCPI error queue.

        Returns:
            SCPIErrors: enum with the SCPI error value.
        """
        return convert_sytem_error(self.system.error())
