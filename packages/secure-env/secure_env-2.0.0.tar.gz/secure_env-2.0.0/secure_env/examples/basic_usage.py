# =============================================================================
# examples/basic_usage.py
# =============================================================================
"""Basic usage examples for secure-env package."""

import os
from secure_env import Secrets

# Example 1: Basic usage
def basic_example():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Initialize with master key
    secrets = Secrets(master_key="my-super-secret-key")
    
    # Store some secrets
    secrets.set("DATABASE_PASSWORD", "SuperSecretPassword123!")
    secrets.set("API_KEY", "sk-1234567890abcdef")
    secrets.set("JWT_SECRET", "jwt-signing-key")
    
    # Store a non-encrypted value
    secrets.set("DEBUG", "true", encrypt=False)
    
    # Retrieve secrets (automatically decrypted)
    db_password = secrets.get("DATABASE_PASSWORD")
    api_key = secrets.get("API_KEY")
    debug_mode = secrets.get("DEBUG")
    
    print(f"Database password: {db_password}")
    print(f"API key: {api_key}")
    print(f"Debug mode: {debug_mode}")
    
    # List all keys and their encryption status
    keys = secrets.list_keys()
    print("\nStored variables:")
    for key, is_encrypted in keys.items():
        status = "encrypted" if is_encrypted else "plain"
        print(f"  {key}: {status}")


# Example 2: Using environment variable for master key
def env_key_example():
    """Example using environment variable for master key."""
    print("\n=== Environment Master Key Example ===")
    
    # Set master key in environment
    os.environ['SECURE_ENV_MASTER_KEY'] = 'env-master-key-123'
    
    # Initialize without explicit master key
    secrets = Secrets(env_file='.env.example')
    
    secrets.set("EMAIL_PASSWORD", "email123")
    secrets.set("REDIS_URL", "redis://localhost:6379")
    
    print(f"Email password: {secrets.get('EMAIL_PASSWORD')}")
    print(f"Redis URL: {secrets.get('REDIS_URL')}")


# Example 3: Working with different data types
def data_types_example():
    """Example with different data types."""
    print("\n=== Data Types Example ===")
    
    secrets = Secrets(master_key="data-types-key", env_file='.env.types')
    
    # Store different types (all converted to strings)
    secrets.set("PORT", 8080)
    secrets.set("RATE_LIMIT", 100.5)
    secrets.set("ENABLED", True)
    secrets.set("CONFIG_JSON", '{"key": "value"}')
    
    # Retrieve values
    port = secrets.get("PORT")
    rate_limit = secrets.get("RATE_LIMIT")
    enabled = secrets.get("ENABLED")
    config = secrets.get("CONFIG_JSON")
    
    print(f"Port: {port} (type: {type(port)})")
    print(f"Rate limit: {rate_limit} (type: {type(rate_limit)})")
    print(f"Enabled: {enabled} (type: {type(enabled)})")
    print(f"Config: {config} (type: {type(config)})")


# Example 4: Export to os.environ
def export_example():
    """Example of exporting to os.environ."""
    print("\n=== Export to os.environ Example ===")
    
    secrets = Secrets(master_key="export-key", env_file='.env.export')
    
    secrets.set("APP_SECRET", "app-secret-123")
    secrets.set("DATABASE_URL", "postgresql://user:pass@localhost/db")
    
    # Export to os.environ (decrypted)
    secrets.export_to_os_environ()
    
    # Now accessible via os.environ
    print(f"APP_SECRET from os.environ: {os.environ.get('APP_SECRET')}")
    print(f"DATABASE_URL from os.environ: {os.environ.get('DATABASE_URL')}")


if __name__ == "__main__":
    try:
        basic_example()
        env_key_example()
        data_types_example()
        export_example()
        
        print("\n=== All examples completed successfully! ===")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()