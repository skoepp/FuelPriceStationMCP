"""Custom exception hierarchy for FuelPriceMCP."""


class FuelPriceMCPError(Exception):
    """Base exception for all FuelPriceMCP errors."""


class ConfigurationError(FuelPriceMCPError):
    """Raised when configuration is invalid or missing."""


class TankerkoenigAPIError(FuelPriceMCPError):
    """Raised when the Tankerkoenig API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class TankerkoenigTimeoutError(FuelPriceMCPError):
    """Raised when the Tankerkoenig API request times out."""


class NoStationsFoundError(FuelPriceMCPError):
    """Raised when no stations match the search criteria."""
