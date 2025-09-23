# =============================================================================
# secure_env/utils.py
# =============================================================================
"""Utility functions for secure-env package."""

import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .exceptions import InvalidKeyError


def generate_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
    """
    Generate a Fernet-compatible key from a password using PBKDF2.
    
    Args:
        password: The master password
        salt: Optional salt bytes. If None, a default salt is used.
    
    Returns:
        bytes: A 32-byte key suitable for Fernet
    
    Raises:
        InvalidKeyError: If password is empty or invalid
    """
    if not password or not isinstance(password, str):
        raise InvalidKeyError("Password must be a non-empty string")
    
    if salt is None:
        # Use a deterministic salt based on password hash for consistency
        salt = hashlib.sha256(password.encode()).digest()[:16]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def generate_random_key() -> str:
    """
    Generate a random Fernet key.
    
    Returns:
        str: Base64-encoded random key
    """
    return Fernet.generate_key().decode()


def is_encrypted_value(value: str) -> bool:
    """
    Check if a value appears to be encrypted (starts with ENC()).
    
    Args:
        value: The value to check
    
    Returns:
        bool: True if value appears encrypted
    """
    return isinstance(value, str) and value.startswith("ENC(") and value.endswith(")")


def extract_encrypted_content(value: str) -> str:
    """
    Extract encrypted content from ENC() wrapper.
    
    Args:
        value: Encrypted value in format ENC(content)
    
    Returns:
        str: The encrypted content without wrapper
    """
    if not is_encrypted_value(value):
        return value
    return value[4:-1]  # Remove "ENC(" and ")"


def wrap_encrypted_content(encrypted_data: str) -> str:
    """
    Wrap encrypted content in ENC() format.
    
    Args:
        encrypted_data: The encrypted data
    
    Returns:
        str: Wrapped encrypted data
    """
    return f"ENC({encrypted_data})"


def safe_file_write(filepath: str, content: str) -> None:
    """
    Safely write content to file with backup.
    
    Args:
        filepath: Path to the file
        content: Content to write
    """
    backup_path = f"{filepath}.backup"
    
    # Create backup if file exists
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Remove backup on success
        if os.path.exists(backup_path):
            os.remove(backup_path)
    except Exception as e:
        # Restore backup on failure
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            os.remove(backup_path)
        raise e