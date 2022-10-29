from enum import Enum
from typing import Optional


class EventStatusEnableBits(Enum):
    """
    Enum for register *ESE?.
    """

    POWER_ON = 7
    COMMAND_ERROR = 5
    EXECUTION_ERROR = 4
    DEVICE_DEPENDENT_ERROR = 3
    QUERY_ERROR = 2
    OPERATION_COMPLETE = 0


class EventStatusBits(Enum):
    """
    Enum for register *ESR?.
    """

    POWER_ON = 7
    COMMAND_ERROR = 5
    EXECUTION_ERROR = 4
    DEVICE_DEPENDENT_ERROR = 3
    QUERY_ERROR = 2
    OPERATION_COMPLETE = 0


class InstrumentStatusBits(Enum):
    """
    Enum for register *STB?.
    """

    BIT_SET_QUESTIONABLE_REGISTER = 5
    ERRORS_IN_ERROR_QUEUE = 3
    BIT_SET_EVENT_STATUS_REGISTER = 2


class QuestionableStatusBits(Enum):
    """
    Enum for register STATUS:QUESTIONABLE:CONDITION?.
    """

    WAVELENGTH_ALREADY_READ = 0
    POWER_OUT_OF_RANGE = 3
    TEMPERATURE_OUT_OF_RANGE = 4
    WAVELENGTH_OUT_OF_RANGE = 5
    PRESSURE_OUT_OF_RANGE = 9
    REFERENCE_LASER_NOT_STABILIZED = 10


class Bits:
    """
    Base class for holding register bit values.
    """

    def __init__(self, value: int, enum, size: int, fault_bits: Optional[tuple] = None):
        self.value: int = value
        self.enum = enum
        self.size: int = size
        self.fault_bits: Optional[tuple] = fault_bits

    def get_set_bits(self) -> tuple:
        """
        Get the set bits in the register.

        Returns:
            tuple: set bits
        """
        return tuple([i for i in range(self.size) if (self.value >> i & 1)])
        # return [i for i in range(self.value.bit_length()) if (self.value >> i & 1)]

    def set_bit(self, bit: int, bit_value: int) -> None:
        """
        Set a bit in the register.

        Args:
            bit (int): bit to set
            bit_value (int): bit set value, either 0 (not set) or 1 (set)
        """
        assert bit_value in [0, 1]
        value = self.value if self.value else 0
        value = value | (1 << bit) if bit_value else value & ~(1 << bit)
        self.value = value

    def get_bit(self, bit: int) -> int:
        """
        Get a bit

        Args:
            bit (int): bit numer to get

        Returns:
            int: bit value, either 0 (not set) or 1 (set)
        """
        return self.value >> bit & 1

    def set_value(self, enum: Enum, val: int):
        """
        Set a register bit value with the enum.

        Args:
            enum (Enum): enum value of bit to set
            val (int): bit set value, either 0 (not set) or 1 (set)
        """
        self.set_bit(enum.value, val)

    def get_value(self, enum: Enum) -> int:
        """
        Get bit value with the enum.

        Args:
            enum (Enum): enum value of the bit to get

        Returns:
            int: bit set value, either 0 (not set) or 1 (set)
        """
        return self.get_bit(enum.value)

    def get_set_values(self) -> tuple:
        """
        Get all set bit enum values.

        Returns:
            tuple: set bit enum values
        """
        return tuple([self.enum(bit).name for bit in self.get_set_bits()])

    @property
    def faults(self) -> tuple:
        """
        Faults active in register.

        Returns:
            tuple: faults active in register by enum value
        """
        if self.fault_bits is None:
            return ()
        else:
            return tuple([self.get_value(fault_bit) for fault_bit in self.fault_bits])

    @property
    def is_ok(self) -> bool:
        """
        Check if no faults active in register

        Returns:
            bool: True if register has no faults, else False
        """
        return len(self.faults) == 0

    def __repr__(self) -> str:
        name = self.enum.__name__.strip("Bits")
        set_values = self.get_set_values()
        repr = f"{name}Register("
        for val in set_values:
            repr += f"{val}, "
        return repr.strip(", ") + ")"


class EventStatusEnableRegister(Bits):
    def __init__(self, value):
        super().__init__(value, EventStatusEnableBits, 8, fault_bits=(5, 4, 3, 2))


class EventStatusRegister(Bits):
    def __init__(self, value):
        super().__init__(value, EventStatusBits, 8, fault_bits=(5, 4, 3, 2))


class InstrumentStatusByte(Bits):
    def __init__(self, value):
        super().__init__(value, InstrumentStatusBits, 6, fault_bits=(3,))


class QuestionableStatusRegister(Bits):
    def __init__(self, value):
        super().__init__(
            value, QuestionableStatusBits, 11, fault_bits=(0, 3, 4, 5, 9, 10)
        )
