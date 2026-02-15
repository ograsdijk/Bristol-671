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