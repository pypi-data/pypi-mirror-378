# =============================================================================
# tests/test_core.py
# =============================================================================
"""Tests for secure_env.core module."""

import unittest
import tempfile
import os
from unittest.mock import patch

from secure_env import Secrets
from secure_env.exceptions import InvalidKeyError, DecryptionError, FileAccessError


class TestSecrets(unittest.TestCase):
    """Test cases for Secrets class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_env_file = os.path.join(self.temp_dir, 'test.env')
        self.master_key = "test-master-key-123"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_master_key(self):
        """Test initialization with master key."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        self.assertIsInstance(secrets, Secrets)
        self.assertTrue(os.path.exists(self.test_env_file))
    
    def test_init_without_master_key_raises_error(self):
        """Test initialization without master key raises error."""
        with self.assertRaises(InvalidKeyError):
            Secrets(env_file=self.test_env_file)
    
    @patch.dict(os.environ, {'SECURE_ENV_MASTER_KEY': 'env-key-123'})
    def test_init_with_env_master_key(self):
        """Test initialization with master key from environment."""
        secrets = Secrets(env_file=self.test_env_file)
        self.assertIsInstance(secrets, Secrets)
    
    def test_set_and_get_encrypted(self):
        """Test setting and getting encrypted values."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        
        secrets.set("TEST_PASSWORD", "secret123")
        retrieved = secrets.get("TEST_PASSWORD")
        
        self.assertEqual(retrieved, "secret123")
    
    def test_set_and_get_unencrypted(self):
        """Test setting and getting unencrypted values."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        
        secrets.set("TEST_CONFIG", "public_value", encrypt=False)
        retrieved = secrets.get("TEST_CONFIG")
        
        self.assertEqual(retrieved, "public_value")
    
    def test_get_with_default(self):
        """Test getting non-existent key with default value."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        
        result = secrets.get("NON_EXISTENT", default="default_value")
        self.assertEqual(result, "default_value")
    
    def test_delete_key(self):
        """Test deleting a key."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        
        secrets.set("TO_DELETE", "value")
        self.assertEqual(secrets.get("TO_DELETE"), "value")
        
        result = secrets.delete("TO_DELETE")
        self.assertTrue(result)
        self.assertIsNone(secrets.get("TO_DELETE"))
    
    def test_list_keys(self):
        """Test listing keys."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        
        secrets.set("ENCRYPTED_KEY", "secret", encrypt=True)
        secrets.set("PLAIN_KEY", "public", encrypt=False)
        
        keys = secrets.list_keys()
        self.assertIn("ENCRYPTED_KEY", keys)
        self.assertIn("PLAIN_KEY", keys)
        self.assertTrue(keys["ENCRYPTED_KEY"])  # Should be encrypted
        self.assertFalse(keys["PLAIN_KEY"])    # Should not be encrypted
    
    def test_change_master_key(self):
        """Test changing master key."""
        secrets = Secrets(
            master_key=self.master_key,
            env_file=self.test_env_file
        )
        
        secrets.set("TEST_SECRET", "secret_value")
        
        # Change master key
        new_key = "new-master-key-456"
        secrets.change_master_key(new_key)
        
        # Should still be able to retrieve the value
        retrieved = secrets.get("TEST_SECRET")
        self.assertEqual(retrieved, "secret_value")


if __name__ == '__main__':
    unittest.main()