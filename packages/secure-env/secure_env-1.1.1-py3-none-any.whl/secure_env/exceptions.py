# =============================================================================
# secure_env/exceptions.py
# =============================================================================
"""Custom exceptions for secure-env package."""


class SecureEnvError(Exception):
    """Base exception for secure-env package."""
    pass


class InvalidKeyError(SecureEnvError):
    """Raised when the master key is invalid."""
    pass


class DecryptionError(SecureEnvError):
    """Raised when decryption fails."""
    pass


class FileAccessError(SecureEnvError):
    """Raised when there are file access issues."""
    pass
