from __future__ import annotations

try:
    import cloudflare as _cf
    _CF_AVAILABLE = True
except ImportError:
    _cf = None  # type: ignore[assignment]
    _CF_AVAILABLE = False

try:
    from cfmanager.core.exceptions import APIError as _APIError
    _APIERROR_AVAILABLE = True
except ImportError:
    _APIError = None  # type: ignore[assignment,misc]
    _APIERROR_AVAILABLE = False


def format_error(exc: Exception) -> str:
    """Return a short, human-readable error message suitable for a TUI notification."""
    if _APIERROR_AVAILABLE and isinstance(exc, _APIError) and exc.__cause__ is not None:
        exc = exc.__cause__

    if _CF_AVAILABLE:
        if isinstance(exc, _cf.AuthenticationError):
            return "Invalid API token — run: cfm config set-token <token>"

        if isinstance(exc, _cf.PermissionDeniedError):
            return "Permission denied — check your API token scopes in the Cloudflare dashboard"

        if isinstance(exc, _cf.NotFoundError):
            return "Resource not found"

        if isinstance(exc, _cf.RateLimitError):
            return "Rate limited — wait a moment, then press r to retry"

        if isinstance(exc, _cf.APITimeoutError):
            return "Request timed out — check your connection"

        if isinstance(exc, _cf.APIConnectionError):
            return "Connection failed — check your internet connection"

        if isinstance(exc, _cf.InternalServerError):
            return "Cloudflare server error — try again later"

        if isinstance(exc, _cf.APIStatusError):
            if exc.errors:
                msg = exc.errors[0].message
                if msg:
                    return msg
            return f"API error ({exc.status_code})"

    msg = str(exc)
    # Strip verbose class prefixes like "APIError: Cloudflare API error getting ...: "
    if ": " in msg:
        prefix, rest = msg.split(": ", 1)
        if len(prefix) < 40:
            msg = rest
    return msg[:150]
