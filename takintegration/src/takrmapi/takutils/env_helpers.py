"""Helpers for reading typed values from environment variables"""

import os
import logging

LOGGER = logging.getLogger(__name__)


def env_float(key: str, default: float, min_value: float = 0.0, max_value: float = 600.0) -> float:
    """Read a float from an environment variable with inclusive bounds [min_value, max_value].

    Raises ValueError immediately if default is outside the allowed range, as that is a
    programming error. Invalid or out-of-range env var values fall back to the default.
    """
    if not min_value <= default <= max_value:
        raise ValueError(f"default {default} is outside allowed range [{min_value}, {max_value}]")
    try:
        value = float(os.getenv(key) or default)
        if not min_value <= value <= max_value:
            raise ValueError(f"{value} out of range [{min_value}, {max_value}]")
        return value
    except (TypeError, ValueError):
        LOGGER.warning("Invalid value for %s, using default %s", key, default)
        return default
