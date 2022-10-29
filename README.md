# Bristol-671
Python interface for the [Bristol 671]("https://www.bristol-inst.com/bristol-instruments-products/wavelength-meters-scientific/671-series-cw-lasers/") wavelength meter.  
Has not been tested with the a connected wavelength meter yet.
## Install
Install Bristol671 with `python setup.py install`
## Code Example
```Python
from astropy import units
from bristol671 import Bristol671, MeasureData, MeasureMethod, PowerUnit

wm = Bristol671(port = None)
# frequency in THz
freq = wm.get_data(MeasureData.FREQUENCY, MeasureMethod.READ)
# frequency in GHz
freq = wm.get_data(MeasureData.FREQUENCY, MeasureMethod.READ, unit = units.GHz)

# start averaging measurement over the last 8 measurements
wm.average_count = 8
wm.average_state = True
freq_avg = wm.get_average_data(MeasureData.FREQUENCY)

# read the event status register and check for faults
esr = wm.event_status_register()
print(esr.get_faults())

# set the wavelength power measurement to mW and read the power
wm.unit_power = PowerUnit.mW
power = wm.get(MeasureData.POWER, MeasureMethod.READ)

# it is also possible to directly call the FETCH, READ or MEASURE functions
wavelength = wm.measure_wavelength()
```