"""Common utilities and constants for TJES PJE MCP servers.

This module provides shared functionality used across multiple MCP servers:
- Environment variable validation and parsing
- Formatting utilities for output display
- Shared constants and configuration values
"""

__version__ = "1.0.0"

from .constants import (
    # Timeout defaults
    DEFAULT_TIMEOUT_SECONDS,
    MIN_TIMEOUT_SECONDS,
    MAX_TIMEOUT_SECONDS,

    # Retry defaults
    DEFAULT_RETRY_ATTEMPTS,
    MIN_RETRY_ATTEMPTS,
    MAX_RETRY_ATTEMPTS,

    # Session defaults
    DEFAULT_SESSION_MAX_AGE_HOURS,
    MIN_SESSION_AGE_HOURS,
    MAX_SESSION_AGE_HOURS,

    # Formatting constants
    BOX_WIDTH,
    ICONS,
)

from .utilities import (
    get_int_env,
    format_box,
    format_key_value,
    format_section,
)

__all__ = [
    # Version
    "__version__",

    # Constants
    "DEFAULT_TIMEOUT_SECONDS",
    "MIN_TIMEOUT_SECONDS",
    "MAX_TIMEOUT_SECONDS",
    "DEFAULT_RETRY_ATTEMPTS",
    "MIN_RETRY_ATTEMPTS",
    "MAX_RETRY_ATTEMPTS",
    "DEFAULT_SESSION_MAX_AGE_HOURS",
    "MIN_SESSION_AGE_HOURS",
    "MAX_SESSION_AGE_HOURS",
    "BOX_WIDTH",
    "ICONS",

    # Utilities
    "get_int_env",
    "format_box",
    "format_key_value",
    "format_section",
]
