"""Application exceptions with messages suitable for the command line."""


class TrackCoderError(Exception):
    """Base class for expected, recoverable application errors."""


class ValidationError(TrackCoderError):
    """Raised when user input or stored data is invalid."""


class StorageError(TrackCoderError):
    """Raised when metrics cannot be read or written safely."""


class CollectionError(TrackCoderError):
    """Raised when an external metrics provider cannot be collected."""


class ConfigurationError(TrackCoderError):
    """Raised when a requested integration is not configured."""
