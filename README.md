# Bristol-671
Python interface for the [Bristol 671](https://www.bristol-inst.com/bristol-instruments-products/wavelength-meters-scientific/671-series-cw-lasers/) wavelength meter.  
Has not been tested with the a connected wavelength meter yet.

## Install
Using uv:

- Requires Python 3.11+
- Create/sync environment: `uv sync`
- Install package in editable mode: `uv pip install -e .`

SCPI common commands are exposed as Pythonic methods:

- `clear_status()` (alias of `CLS()`)
- `reset()` (alias of `RST()`)
- `save_state()` (alias of `SAV()`)
- `restore_state()` (alias of `RCL()`)

## API Reference (public methods)

### Main class

- `Bristol671(port, timeout=2.0)` — create an instrument connection.
- `drain_error_queue(raise_on_error=False, max_reads=32)` — drain `SYSTEM:ERROR?` until `NO_ERROR`.
- `get_data(data, method, unit=None)` — unified read/fetch/measure API with optional unit conversion.
- `get_average_data(data)` — read averaged value for `POWER`, `FREQUENCY`, `WAVELENGTH`, or `WAVENUMBER`.

### SCPI command helpers

- `clear_status()` / `CLS()` — clear status/event registers and error queue (`*CLS`).
- `restore_state()` / `RCL()` — restore saved instrument state (`*RCL`).
- `reset()` / `RST()` — reset instrument (`*RST`).
- `save_state()` / `SAV()` — save instrument state (`*SAV`).

### Direct measurement methods

- `fetch_environment()`, `read_environment()`, `measure_environment()` — return `Environment(temperature, pressure)`.
- `fetch_wavelength()`, `read_wavelength()`, `measure_wavelength()` — wavelength in nm.
- `fetch_frequency()`, `read_frequency()`, `measure_frequency()` — frequency in THz.
- `fetch_power()`, `read_power()`, `measure_power()` — power in current `unit_power` (`mW` or `dBm`).
- `fetch_wavenumber()`, `read_wavenumber()`, `measure_wavenumber()` — wavenumber in cm^-1.
- `fetch_all()`, `read_all()`, `measure_all()` — return `WavemeterData(scan_index, instrument_status, wavelength, power)`.

### Useful properties

- `average_state` — enable/disable averaging (`True`/`False`).
- `average_count` — averaging sample count.
- `unit_power` — active power unit (`PowerUnit.mW` or `PowerUnit.dBm`).
- `system_error` — current SCPI error as `SCPIErrors` enum.
- `system_error_message` — current SCPI error message string.

### Register and status properties

- `event_status_enable_register` — typed `*ESE` register view.
- `event_status_register` — typed `*ESR` register view.
- `status_register` — typed `*STB` status byte view.
- `questionable_condition_register` — typed questionable-condition register view.
- `ESE` — raw event-status-enable byte (read/write).
- `ESR` — raw event-status byte (read).
- `OPC` — operation complete bit query (`*OPC?`).
- `STB` — raw status byte (read).

### Exported enums and exceptions

- Enums: `MeasureData`, `MeasureMethod`, `PowerUnit`.
- Exceptions: `BristolError`, `BristolParseError`, `SCPICommandError`.

## Typing support

This package ships a `py.typed` marker (PEP 561), so type checkers can use its inline type hints.

## API notes

- Uppercase SCPI-style commands (`CLS`, `RCL`, `RST`, `SAV`) are supported.
- Pythonic aliases (`clear_status`, `restore_state`, `reset`, `save_state`) call the same commands.
- `get_data(..., unit=...)` unit conversion is supported for `POWER`, `FREQUENCY`, `WAVELENGTH`, and `WAVENUMBER`.
- `ENVIRONMENT` and `ALL` are intentionally not converted via `unit`.

## Changelog

### 0.2.0

- Migrated unit conversion to `pint`.
- Added typed package marker (`py.typed`).
- Added explicit package exceptions (`BristolError`, `BristolParseError`, `SCPICommandError`).

## Code Example
```Python
from bristol_671 import Bristol671, MeasureData, MeasureMethod, PowerUnit

wm = Bristol671(port = None)
# frequency in THz
freq = wm.get_data(MeasureData.FREQUENCY, MeasureMethod.READ)
# frequency in GHz
freq = wm.get_data(MeasureData.FREQUENCY, MeasureMethod.READ, unit = "GHz")

# start averaging measurement over the last 8 measurements
wm.average_count = 8
wm.average_state = True
freq_avg = wm.get_average_data(MeasureData.FREQUENCY)

# read the event status register and check for faults
esr = wm.event_status_register
print(esr.faults)

# set the wavelength power measurement to mW and read the power
wm.unit_power = PowerUnit.mW
power = wm.get_data(MeasureData.POWER, MeasureMethod.READ)

# it is also possible to directly call the FETCH, READ or MEASURE functions
wavelength = wm.measure_wavelength()
```