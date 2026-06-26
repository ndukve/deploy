"""Database-layer exceptions."""


class NotFound(Exception):
    """Requested record does not exist."""


class Deleted(Exception):
    """Requested record exists but is deleted or otherwise inactive."""
