from enum import Enum


class MeasureData(Enum):
    POWER = 0
    FREQUENCY = 1
    WAVELENGTH = 2
    WAVENUMBER = 3
    ENVIRONMENT = 4
    ALL = 5


class MeasureMethod(Enum):
    FETCH = 0
    READ = 1
    MEASURE = 2


class PowerUnit(Enum):
    dBm = 0
    mW = 1
