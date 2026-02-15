class BristolError(Exception):
    """Base exception for Bristol-671 package errors."""


class BristolParseError(BristolError, ValueError):
    """Raised when instrument response parsing fails."""


class SCPICommandError(BristolError):
    """Raised when invalid SCPI command inputs are provided."""
