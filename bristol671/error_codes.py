from enum import Enum


class SCPIErrors(Enum):
    """
    Enum for error codes returned by SYSTEM:ERROR?
    """

    NO_ERROR = 0
    INVALID_CHARACTER = -101
    SYNTAX_ERROR = -102
    INVALID_SEPARATOR = -103
    DATA_TYPE_ERROR = -104
    PARAMETER_ERROR = -220
    SETTINGS_CONFLICT = -221
    DATA_OUT_OF_RANGE = -222
    DATA_CORRUPT_OR_STALE = -230

