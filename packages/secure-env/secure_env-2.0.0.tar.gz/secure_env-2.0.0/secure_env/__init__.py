# =============================================================================
# secure_env/__init__.py
# =============================================================================
"""
Secure Environment Variables Manager

A simple and secure way to manage environment variables with AES encryption.
"""

__version__ = "2.0.0"
__author__ = "Mohamed Ndiaye"
__email__ = "mintok2000@gmail.com"

from .core import Secrets
from .exceptions import SecureEnvError, InvalidKeyError, DecryptionError

__all__ = ['Secrets', 'SecureEnvError', 'InvalidKeyError', 'DecryptionError']
