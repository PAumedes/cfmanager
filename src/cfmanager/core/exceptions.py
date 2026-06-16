class CFManagerError(Exception):
    """Base exception for all CFManager errors."""
    pass

class ConfigError(CFManagerError):
    """Configuration related errors."""
    pass

class APIError(CFManagerError):
    """Cloudflare API related errors."""
    pass

class ValidationError(CFManagerError):
    """Input validation related errors."""
    pass
