"""Shared constants for TJES PJE MCP servers.

This module contains all configuration constants used across the MCP servers,
eliminating magic numbers and providing a single source of truth.
"""

# =============================================================================
# TIMEOUT CONFIGURATION
# =============================================================================

DEFAULT_TIMEOUT_SECONDS: int = 30
"""Default timeout for HTTP requests in seconds."""

MIN_TIMEOUT_SECONDS: int = 5
"""Minimum allowed timeout value in seconds."""

MAX_TIMEOUT_SECONDS: int = 120
"""Maximum allowed timeout value in seconds."""


# =============================================================================
# RETRY CONFIGURATION
# =============================================================================

DEFAULT_RETRY_ATTEMPTS: int = 3
"""Default number of retry attempts for failed requests."""

MIN_RETRY_ATTEMPTS: int = 1
"""Minimum allowed retry attempts."""

MAX_RETRY_ATTEMPTS: int = 10
"""Maximum allowed retry attempts."""


# =============================================================================
# SESSION CONFIGURATION
# =============================================================================

DEFAULT_SESSION_MAX_AGE_HOURS: int = 8
"""Default maximum age for browser sessions in hours."""

MIN_SESSION_AGE_HOURS: int = 1
"""Minimum allowed session age in hours."""

MAX_SESSION_AGE_HOURS: int = 24
"""Maximum allowed session age in hours."""


# =============================================================================
# FORMATTING CONSTANTS
# =============================================================================

BOX_WIDTH: int = 70
"""Width of formatted box output in characters."""


# =============================================================================
# ICONS AND SYMBOLS
# =============================================================================

ICONS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "clock": "🕐",
    "check": "✓",
    "cross": "✗",
    "arrow": "→",
    "bullet": "•",
    "certificate": "🔐",
    "session": "🔑",
    "browser": "🌐",
}
"""Icons used for formatted output display."""


# =============================================================================
# HTTP STATUS CODES
# =============================================================================

HTTP_OK: int = 200
"""HTTP status code for successful requests."""

HTTP_UNAUTHORIZED: int = 401
"""HTTP status code for unauthorized access."""

HTTP_FORBIDDEN: int = 403
"""HTTP status code for forbidden access."""

HTTP_NOT_FOUND: int = 404
"""HTTP status code for resource not found."""

HTTP_INTERNAL_SERVER_ERROR: int = 500
"""HTTP status code for internal server errors."""


# =============================================================================
# CERTIFICATE CONFIGURATION
# =============================================================================

CERT_TYPE_A1: str = "A1"
"""Certificate type A1 (local PFX file)."""

CERT_TYPE_A3: str = "A3"
"""Certificate type A3 (smart card or cloud)."""

CERT_TYPE_SAFE_ID: str = "SAFE_ID"
"""Certificate type Safe ID (cloud-based A3)."""


# =============================================================================
# FILE EXTENSIONS
# =============================================================================

CERT_EXTENSIONS = {
    ".pfx": "PFX (PKCS#12)",
    ".p12": "P12 (PKCS#12)",
    ".pem": "PEM",
}
"""Supported certificate file extensions."""


# =============================================================================
# SESSION FILE NAMES
# =============================================================================

SESSION_COOKIES_FILE: str = "cookies.json"
"""Filename for session cookies storage."""

SESSION_STATE_FILE: str = "state.json"
"""Filename for session state storage."""

SESSION_METADATA_FILE: str = "metadata.json"
"""Filename for session metadata storage."""


# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

DEFAULT_CACHE_TTL_SECONDS: int = 3600
"""Default cache TTL (time to live) in seconds (1 hour)."""

MIN_CACHE_TTL_SECONDS: int = 60
"""Minimum cache TTL in seconds (1 minute)."""

MAX_CACHE_TTL_SECONDS: int = 86400
"""Maximum cache TTL in seconds (24 hours)."""
