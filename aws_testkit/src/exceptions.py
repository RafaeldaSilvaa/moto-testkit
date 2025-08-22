class MotoTestKitError(Exception):
    """Base exception for aws_testkit."""

class ClientNotStartedError(MotoTestKitError):
    """Raised when attempting to get clients in unexpected state."""
