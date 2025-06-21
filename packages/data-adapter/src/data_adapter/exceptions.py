class DataAdapterError(Exception):
    """Base exception class for the data adapter."""
    pass


class ConfigurationError(DataAdapterError):
    """Raised when there is a configuration error."""
    pass


class APIError(DataAdapterError):
    """Raised when the API returns an error."""
    pass


class ParserError(DataAdapterError):
    """Raised when there is an error parsing data."""
    pass 