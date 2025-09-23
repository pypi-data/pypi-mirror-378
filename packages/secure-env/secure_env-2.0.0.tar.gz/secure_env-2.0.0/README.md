# 🔐 Secure-Env

[![PyPI version](https://badge.fury.io/py/secure-env.svg)](https://badge.fury.io/py/secure-env)
[![Python Support](https://img.shields.io/pypi/pyversions/secure-env.svg)](https://pypi.org/project/secure-env/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/secure-env)](https://pepy.tech/project/secure-env)
[![Tests](https://github.com/Moesthetics-code/secure-env/workflows/Tests/badge.svg)](https://github.com/Moesthetics-code/secure-env/actions)
[![Coverage](https://codecov.io/gh/yourname/secure-env/branch/main/graph/badge.svg)](https://codecov.io/gh/yourname/secure-env)

**A simple and secure environment variables manager with AES-256 encryption.**

Secure-Env solves the critical problem of storing passwords, API keys, and other secrets in plain text within `.env` files or directly in source code. It provides an elegant solution with transparent encryption and a simple API.

## 🌟 Why Secure-Env?

### ❌ **Current Problems**$$
```bash
# Classic .env file - DANGEROUS!
DATABASE_PASSWORD=SuperSecretPassword123!
API_KEY=sk-1234567890abcdef
JWT_SECRET=my-jwt-signing-key
```

### ✅ **Secure-Env Solution**
```bash
# Secure .env file
DATABASE_PASSWORD=ENC(gAAAAABh_9x2K8L5vV6K2oJ3cE...)
API_KEY=ENC(gAAAAABh_8y3L9M6wW7L3pK4dF...)
JWT_SECRET=ENC(gAAAAABh_7z4M0N7xX8M4qL5eG...)
DEBUG=true
```

## 🚀 Installation

```bash
# Install from PyPI
pip install secure-env

# Install with development dependencies
pip install secure-env[dev]

# From source code
git clone https://github.com/Moesthetics-code/secure-env.git
cd secure-env
pip install -e .
```

### Verify Installation
```bash
# Check version
secure-env --version

# Test Python import
python -c "import secure_env; print(secure_env.__version__)"
```

## ⚡ Quick Start

### 1. Initial Setup

```bash
# Initialize a secure environment
secure-env init --generate-key

# Output:
# 🔑 Generated master key: 8mJeOQ-Xd9u2vFq4GhKlMpNo5r8t6w3z
# ⚠️  IMPORTANT: Save this key securely!

# Set master key (recommended)
export SECURE_ENV_MASTER_KEY='8mJeOQ-Xd9u2vFq4GhKlMpNo5r8t6w3z'
```

### 2. Add Secrets

```bash
# Add a password (encrypted)
secure-env set DATABASE_PASSWORD
🔒 Enter value for DATABASE_PASSWORD: ****

# Or directly with value
secure-env set API_KEY 'sk-1234567890abcdef'
✅ Set API_KEY (encrypted)

# Add unencrypted variable
secure-env set DEBUG true --no-encrypt
✅ Set DEBUG (plain)
```

### 3. Usage

```bash
# List all variables
secure-env list

# Get a variable
secure-env get DATABASE_PASSWORD

# Export for usage
eval $(secure-env export --format env)
echo $DATABASE_PASSWORD  # Shows decrypted value
```

### 4. Python Usage

```python
from secure_env import Secrets

# Initialize with master key
secrets = Secrets(master_key="your-master-key")

# Or use SECURE_ENV_MASTER_KEY environment variable
secrets = Secrets()

# Store secrets
secrets.set("DATABASE_PASSWORD", "SuperSecretPassword123!")
secrets.set("API_KEY", "sk-1234567890abcdef")

# Retrieve secrets (automatically decrypted)
db_password = secrets.get("DATABASE_PASSWORD")
api_key = secrets.get("API_KEY")

print(f"DB Password: {db_password}")
print(f"API Key: {api_key}")
```

## 📚 CLI Commands Documentation

### `secure-env init`

**Description:** Initialize a new secure environment.

**Syntax:**
```bash
secure-env init [OPTIONS]
```

**Options:**
- `--generate-key` : Automatically generate a random master key
- `--force` : Force overwrite of existing .env file
- `--env-file PATH`, `-f PATH` : Specify .env file (default: `.env`)

**Examples:**
```bash
# Basic initialization (prompts for master key)
secure-env init

# Initialize with key generation
secure-env init --generate-key

# Initialize in specific file
secure-env init -f .env.production --generate-key

# Force overwrite
secure-env init --force
```

**Example Output:**
```
🔧 Initializing secure environment...
🔑 Generated master key: 8mJeOQ-Xd9u2vFq4GhKlMpNo5r8t6w3z
⚠️  IMPORTANT: Save this key securely! You'll need it to decrypt your secrets.
✅ Initialized secure environment in .env

💡 To use this environment, set:
   export SECURE_ENV_MASTER_KEY='8mJeOQ-Xd9u2vFq4GhKlMpNo5r8t6w3z'
```

---

### `secure-env set`

**Description:** Set an environment variable (encrypted by default).

**Syntax:**
```bash
secure-env set KEY [VALUE] [OPTIONS]
```

**Arguments:**
- `KEY` : Variable name (required)
- `VALUE` : Variable value (optional, prompts if omitted)

**Options:**
- `--no-encrypt` : Store value as plain text
- `--no-prompt` : Don't prompt for value if omitted
- `--env-file PATH`, `-f PATH` : .env file to use
- `--master-key KEY`, `-k KEY` : Master key (not recommended)

**Examples:**
```bash
# Set with secure prompt
secure-env set DATABASE_PASSWORD
🔒 Enter value for DATABASE_PASSWORD: ****

# Set with direct value
secure-env set API_KEY 'sk-1234567890abcdef'

# Set unencrypted variable
secure-env set DEBUG true --no-encrypt
secure-env set PORT 8080 --no-encrypt

# Set in specific file
secure-env set -f .env.prod SECRET_KEY 'prod-secret'

# Script usage (no prompt)
echo "secret-value" | secure-env set MY_SECRET --no-prompt
```

**Supported Data Types:**
```bash
# Strings
secure-env set MESSAGE "Hello World!"

# Numbers (stored as strings)
secure-env set PORT 8080
secure-env set RATE_LIMIT 100.5

# Booleans (stored as strings)
secure-env set ENABLED true
secure-env set DEBUG false

# JSON (stored as string)
secure-env set CONFIG '{"host": "localhost", "port": 5432}'

# URLs with special characters
secure-env set DATABASE_URL 'postgresql://user:pass@host:5432/db'
```

---

### `secure-env get`

**Description:** Retrieve an environment variable value.

**Syntax:**
```bash
secure-env get KEY [OPTIONS]
```

**Arguments:**
- `KEY` : Variable name to retrieve

**Options:**
- `--show-encrypted` : Show both encrypted and decrypted versions
- `--quiet`, `-q` : Show only value (for scripts)
- `--env-file PATH`, `-f PATH` : .env file to use
- `--master-key KEY`, `-k KEY` : Master key

**Examples:**
```bash
# Normal retrieval
secure-env get DATABASE_PASSWORD
# Output: DATABASE_PASSWORD: SuperSecretPassword123!

# Quiet mode for scripts
DB_PASS=$(secure-env get DATABASE_PASSWORD --quiet)
echo "Password: $DB_PASS"

# Show encrypted and decrypted versions
secure-env get API_KEY --show-encrypted
# 🔒 API_KEY (encrypted): ENC(gAAAAABh_8y3L9M6wW...)
# 🔓 API_KEY (decrypted): sk-1234567890abcdef

# Get from specific file
secure-env get -f .env.staging SECRET_KEY
```

**Return Codes:**
- `0` : Success
- `1` : Variable not found or decryption error

**Error Handling:**
```bash
# Non-existent variable
secure-env get NON_EXISTENT
# ❌ Variable 'NON_EXISTENT' not found
# Return code: 1

# Decryption error (wrong key)
secure-env get ENCRYPTED_VAR
# ❌ Failed to decrypt 'ENCRYPTED_VAR' - wrong master key?
# Return code: 1
```

---

### `secure-env list`

**Description:** List all environment variables with their encryption status.

**Syntax:**
```bash
secure-env list [OPTIONS]
```

**Options:**
- `--show-values` : Show variable values
- `--format FORMAT` : Output format (`table` or `json`)
- `--env-file PATH`, `-f PATH` : .env file to use
- `--master-key KEY`, `-k KEY` : Master key

**Examples:**
```bash
# Basic list
secure-env list
# Key              | Value/Status
# -----------------|-------------
# API_KEY          | 🔒 encrypted
# DATABASE_PASSWORD| 🔒 encrypted
# DEBUG            | 📄 plain
# PORT             | 📄 plain

# List with values
secure-env list --show-values
# Key              | Value/Status
# -----------------|-------------
# API_KEY 🔒       | sk-1234567890abcdef
# DATABASE_PASSWORD🔒| SuperSecretPassword123!
# DEBUG 📄         | true
# PORT 📄          | 8080

# JSON format
secure-env list --format json
# {
#   "API_KEY": true,
#   "DATABASE_PASSWORD": true,
#   "DEBUG": false,
#   "PORT": false
# }

# JSON format with values
secure-env list --show-values --format json
# {
#   "API_KEY 🔒": "sk-1234567890abcdef",
#   "DATABASE_PASSWORD 🔒": "SuperSecretPassword123!",
#   "DEBUG 📄": "true",
#   "PORT 📄": "8080"
# }
```

**Icon Legend:**
- 🔒 : Encrypted variable
- 📄 : Plain text variable
- ❌ : Decryption error

---

### `secure-env delete`

**Description:** Delete an environment variable.

**Syntax:**
```bash
secure-env delete KEY [OPTIONS]
```

**Arguments:**
- `KEY` : Variable name to delete

**Options:**
- `--force` : Delete without confirmation
- `--env-file PATH`, `-f PATH` : .env file to use
- `--master-key KEY`, `-k KEY` : Master key

**Examples:**
```bash
# Delete with confirmation
secure-env delete OLD_API_KEY
❓ Delete 'OLD_API_KEY'? (y/N): y
✅ Deleted 'OLD_API_KEY'

# Force delete (for scripts)
secure-env delete TEMP_SECRET --force
✅ Deleted 'TEMP_SECRET'

# Delete from specific file
secure-env delete -f .env.test TEST_VAR --force

# Attempt to delete non-existent variable
secure-env delete NON_EXISTENT --force
❌ Variable 'NON_EXISTENT' not found
```

---

### `secure-env export`

**Description:** Export variables in different formats for external use.

**Syntax:**
```bash
secure-env export [OPTIONS]
```

**Options:**
- `--format FORMAT` : Export format (`env`, `json`, `dotenv`)
- `--skip-failed` : Skip variables that cannot be decrypted
- `--env-file PATH`, `-f PATH` : .env file to use
- `--master-key KEY`, `-k KEY` : Master key

**Available Formats:**

#### 1. Format `env` (default) - Shell variables
```bash
secure-env export --format env
# export DATABASE_PASSWORD="SuperSecretPassword123!"
# export API_KEY="sk-1234567890abcdef"
# export DEBUG="true"
# export PORT="8080"

# Shell usage
eval $(secure-env export --format env)
echo $DATABASE_PASSWORD  # SuperSecretPassword123!
```

#### 2. Format `json` - JSON object
```bash
secure-env export --format json
# {
#   "DATABASE_PASSWORD": "SuperSecretPassword123!",
#   "API_KEY": "sk-1234567890abcdef",
#   "DEBUG": "true",
#   "PORT": "8080"
# }

# Usage with jq
secure-env export --format json | jq -r '.DATABASE_PASSWORD'
```

#### 3. Format `dotenv` - Decrypted .env format
```bash
secure-env export --format dotenv
# DATABASE_PASSWORD="SuperSecretPassword123!"
# API_KEY=sk-1234567890abcdef
# DEBUG=true
# PORT=8080

# Redirect to file
secure-env export --format dotenv > .env.decrypted
```

**Advanced Examples:**
```bash
# Export with error handling
secure-env export --format env --skip-failed

# Export from production environment
secure-env export -f .env.prod --format json

# Pipeline usage
secure-env export --format env | grep DATABASE

# Export for Docker
secure-env export --format env > docker.env
docker run --env-file docker.env myapp
```

---

### `secure-env import`

**Description:** Import variables from an external file.

**Syntax:**
```bash
secure-env import FILE [OPTIONS]
```

**Arguments:**
- `FILE` : File to import (.env format)

**Options:**
- `--overwrite` : Overwrite existing variables
- `--no-encrypt` : Import variables as plain text
- `--env-file PATH`, `-f PATH` : Destination .env file
- `--master-key KEY`, `-k KEY` : Master key

**Supported File Formats:**
```bash
# Standard .env format
KEY1=value1
KEY2="value with spaces"
KEY3='single quoted'

# With comments (ignored)
# Database configuration
DATABASE_URL=postgresql://localhost/myapp
DATABASE_PASSWORD=secret123

# Empty variables (ignored)
EMPTY_VAR=
```

**Examples:**
```bash
# Basic import (encrypts variables)
secure-env import backup.env
✅ Imported 5 variables
⚠️  Skipped 2 items

# Import as plain text
secure-env import config.env --no-encrypt

# Import with overwrite
secure-env import new-secrets.env --overwrite

# Import to specific file
secure-env import -f .env.staging staging-config.env

# Import with detailed report
secure-env import large-config.env
# ⚠️  Skipping line 15: Invalid format
# ⚠️  Skipping DATABASE_URL: already exists (use --overwrite)
# ✅ Imported 23 variables
# ⚠️  Skipped 3 items
```

**Conflict Handling:**
```bash
# Without --overwrite: skip existing variables
secure-env import config.env
# ⚠️  Skipping API_KEY: already exists (use --overwrite)

# With --overwrite: replace existing variables
secure-env import config.env --overwrite
# ✅ Overwritten API_KEY
```

---

### `secure-env rotate-key`

**Description:** Rotate the master key (re-encrypt all variables).

**Syntax:**
```bash
secure-env rotate-key [OPTIONS]
```

**Options:**
- `--new-key KEY` : Specify new master key
- `--generate-new` : Automatically generate new key
- `--env-file PATH`, `-f PATH` : .env file to process
- `--master-key KEY`, `-k KEY` : Current master key

**Examples:**
```bash
# Rotate with automatic generation
secure-env rotate-key --generate-new
🔄 Rotating master key...
🔑 Generated new master key: nTq7sU-Yg0v3xGr5IlPnOqNo6t9w4z2A
✅ Master key rotated successfully!

💡 Update your environment:
   export SECURE_ENV_MASTER_KEY='nTq7sU-Yg0v3xGr5IlPnOqNo6t9w4z2A'

# Rotate to specific key
secure-env rotate-key --new-key "my-new-master-key-2024"
🔄 Rotating master key...
✅ Master key rotated successfully!

# Interactive rotation (prompts for new key)
secure-env rotate-key
🔄 Rotating master key...
🔑 Enter new master key: ****
✅ Master key rotated successfully!
```

**Rotation Process:**
1. Decrypt all variables with old key
2. Generate/get new key
3. Re-encrypt all variables with new key
4. Update .env file

**Security:**
- Rotation is atomic (all or nothing)
- Automatic backup on error
- New key validation before applying

---

### `secure-env check`

**Description:** Check environment file integrity and decryption validity.

**Syntax:**
```bash
secure-env check [OPTIONS]
```

**Options:**
- `--env-file PATH`, `-f PATH` : .env file to check
- `--master-key KEY`, `-k KEY` : Master key

**Examples:**
```bash
# Basic check
secure-env check
🔍 Checking .env...
📊 Total variables: 10
🔒 Encrypted: 7
📄 Plain text: 3
✅ All encrypted variables can be decrypted successfully!

# Check with problems
secure-env check
🔍 Checking .env...
📊 Total variables: 8
🔒 Encrypted: 5
📄 Plain text: 3

❌ Failed to decrypt 2 variables:
   - OLD_API_KEY
   - CORRUPTED_SECRET

# Check specific file
secure-env check -f .env.production
```

**Reported Information:**
- Total number of variables
- Number of encrypted vs plain text variables
- Variables that cannot be decrypted
- Overall integrity status

**Return Codes:**
- `0` : All decryptions successful
- `1` : One or more variables cannot be decrypted

---

## 🐍 Detailed Python API

### `Secrets` Class

#### Constructor

```python
class Secrets:
    def __init__(
        self,
        master_key: Optional[str] = None,
        env_file: str = '.env',
        auto_create: bool = True
    )
```

**Parameters:**
- `master_key` : Master key for encryption. If `None`, uses `SECURE_ENV_MASTER_KEY`
- `env_file` : Path to .env file (default: `.env`)
- `auto_create` : Create file if it doesn't exist (default: `True`)

**Exceptions:**
- `InvalidKeyError` : Invalid or missing master key
- `FileAccessError` : File access problem

**Example:**
```python
from secure_env import Secrets

# With explicit key
secrets = Secrets(master_key="my-master-key")

# With environment variable
import os
os.environ['SECURE_ENV_MASTER_KEY'] = 'my-key'
secrets = Secrets()

# Custom file
secrets = Secrets(
    master_key="key",
    env_file=".env.production",
    auto_create=False
)
```

#### Main Methods

##### `set(key, value, encrypt=True)`

Set an environment variable.

```python
def set(self, key: str, value: Union[str, int, float, bool], encrypt: bool = True) -> None
```

**Parameters:**
- `key` : Variable name
- `value` : Variable value (converted to string)
- `encrypt` : If `True`, encrypt the value

**Examples:**
```python
# Automatic encryption
secrets.set("DATABASE_PASSWORD", "secret123")
secrets.set("API_KEY", "sk-1234567890abcdef")

# Different types (converted to strings)
secrets.set("PORT", 8080)
secrets.set("RATE_LIMIT", 100.5)
secrets.set("DEBUG", True)

# Plain text
secrets.set("PUBLIC_URL", "https://myapp.com", encrypt=False)

# Complex data
secrets.set("CONFIG", '{"host": "localhost", "port": 5432}')
```

##### `get(key, default=None, auto_decrypt=True)`

Retrieve an environment variable.

```python
def get(self, key: str, default: Any = None, auto_decrypt: bool = True) -> Any
```

**Parameters:**
- `key` : Variable name
- `default` : Default value if key doesn't exist
- `auto_decrypt` : Automatically decrypt encrypted values

**Examples:**
```python
# Normal retrieval
password = secrets.get("DATABASE_PASSWORD")  # "secret123"

# With default value
port = secrets.get("PORT", default=8080)

# Without auto-decryption
encrypted_value = secrets.get("API_KEY", auto_decrypt=False)
# Returns: "ENC(gAAAAABh...)"

# Type handling
port = int(secrets.get("PORT", "8080"))
debug = secrets.get("DEBUG", "false").lower() == "true"
config = json.loads(secrets.get("CONFIG", "{}"))
```

##### `delete(key)`

Delete a variable.

```python
def delete(self, key: str) -> bool
```

**Returns:** `True` if key existed and was deleted, `False` otherwise.

```python
# Deletion
if secrets.delete("OLD_API_KEY"):
    print("Key deleted")
else:
    print("Key not found")
```

##### `list_keys(show_encrypted=True)`

List all keys with their encryption status.

```python
def list_keys(self, show_encrypted: bool = True) -> Dict[str, bool]
```

**Examples:**
```python
# With encryption status
keys = secrets.list_keys()
# {"API_KEY": True, "DEBUG": False, "PORT": False}

for key, is_encrypted in keys.items():
    status = "🔒" if is_encrypted else "📄"
    print(f"{key} {status}")

# Simple list
keys = secrets.list_keys(show_encrypted=False)
# ["API_KEY", "DEBUG", "PORT"]
```

##### `export_to_os_environ(decrypt_all=True)`

Export to `os.environ`.

```python
def export_to_os_environ(self, decrypt_all: bool = True) -> None
```

**Example:**
```python
import os

# Export with decryption
secrets.export_to_os_environ()
print(os.environ['DATABASE_PASSWORD'])  # "secret123"

# Export without decryption (keep encrypted values)
secrets.export_to_os_environ(decrypt_all=False)
print(os.environ['API_KEY'])  # "ENC(gAAAAA...)"
```

##### `change_master_key(new_master_key)`

Change master key and re-encrypt all variables.

```python
def change_master_key(self, new_master_key: str) -> None
```

**Example:**
```python
# Key rotation
secrets.change_master_key("new-master-key-2024")

# Encrypted variables are automatically re-encrypted
# with the new key
```

#### Utility Methods

##### `encrypt(plaintext)` and `decrypt(encrypted_data)`

Manual encryption/decryption.

```python
# Manual encryption
encrypted = secrets.encrypt("secret-data")
print(encrypted)  # "gAAAAABh..."

# Manual decryption
decrypted = secrets.decrypt(encrypted)
print(decrypted)  # "secret-data"
```

##### `reload()`

Reload variables from file.

```python
# External modification of .env file
# then reload
secrets.reload()
```

### Exceptions

```python
from secure_env.exceptions import (
    SecureEnvError,      # Base exception
    InvalidKeyError,     # Invalid master key
    DecryptionError,     # Decryption failure
    FileAccessError      # File access problem
)

try:
    secrets = Secrets(master_key="wrong-key")
    value = secrets.get("ENCRYPTED_VAR")
except InvalidKeyError:
    print("Invalid master key")
except DecryptionError:
    print("Cannot decrypt")
except FileAccessError:
    print("File access problem")
except SecureEnvError as e:
    print(f"General error: {e}")
```

## 🔧 Integrations and Use Cases

### Django Integration

```python
# settings.py
import os
from secure_env import Secrets

# Initialize
secrets = Secrets()

# Django configuration
SECRET_KEY = secrets.get('DJANGO_SECRET_KEY')
DEBUG = secrets.get('DJANGO_DEBUG', 'False').lower() == 'true'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': secrets.get('DB_NAME'),
        'USER': secrets.get('DB_USER'),
        'PASSWORD': secrets.get('DB_PASSWORD'),
        'HOST': secrets.get('DB_HOST', 'localhost'),
        'PORT': secrets.get('DB_PORT', '5432'),
    }
}

# Email configuration
EMAIL_HOST_PASSWORD = secrets.get('EMAIL_PASSWORD')

# External APIs
STRIPE_SECRET_KEY = secrets.get('STRIPE_SECRET_KEY')
AWS_SECRET_ACCESS_KEY = secrets.get('AWS_SECRET_KEY')
```

### Flask Integration

```python
# config.py
from secure_env import Secrets

class Config:
    def __init__(self):
        self.secrets = Secrets()
    
    SECRET_KEY = property(lambda self: self.secrets.get('FLASK_SECRET_KEY'))
    DATABASE_URI = property(lambda self: self.secrets.get('DATABASE_URL'))
    MAIL_PASSWORD = property(lambda self: self.secrets.get('MAIL_PASSWORD'))

# app.py
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config())
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install application
COPY . /app
WORKDIR /app
RUN pip install secure-env

# Startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

```bash
#!/bin/bash
# entrypoint.sh

# Check for master key
if [ -z "$SECURE_ENV_MASTER_KEY" ]; then
    echo "❌ SECURE_ENV_MASTER_KEY is required"
    exit 1
fi

# Check integrity
secure-env check
if [ $? -ne 0 ]; then
    echo "❌ Environment check failed"
    exit 1
fi

# Export variables
eval $(secure-env export --format env)

# Start application
exec python app.py
```

### CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install secure-env
      run: pip install secure-env
    
    - name: Setup secrets
      env:
        SECURE_ENV_MASTER_KEY: ${{ secrets.PRODUCTION_MASTER_KEY }}
      run: |
        # Check secrets integrity
        secure-env check -f .env.production
        
        # Export for application
        secure-env export -f .env.production --format dotenv > .env.deploy
    
    - name: Deploy application
      run: |
        # Deploy with secrets
        ./deploy.sh
```

### Multi-Environment Management

```bash
# File structure
.env.development    # Local development
.env.staging       # Testing environment
.env.production    # Production

# Management scripts
#!/bin/bash
# setup-env.sh

ENV=${1:-development}
ENV_FILE=".env.${ENV}"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file $ENV_FILE not found"
    exit 1
fi

echo "🔧 Setting up $ENV environment..."

# Check integrity
secure-env check -f "$ENV_FILE"

# Export variables
eval $(secure-env export -f "$ENV_FILE" --format env)

echo "✅ Environment $ENV ready"
```

### FastAPI Integration

```python
# app.py
from fastapi import FastAPI
from secure_env import Secrets
import uvicorn

app = FastAPI()
secrets = Secrets()

# Configuration
DATABASE_URL = secrets.get("DATABASE_URL")
JWT_SECRET = secrets.get("JWT_SECRET_KEY")
REDIS_URL = secrets.get("REDIS_URL")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "secrets_loaded": True}

if __name__ == "__main__":
    # Server configuration
    host = secrets.get("HOST", "0.0.0.0")
    port = int(secrets.get("PORT", "8000"))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=secrets.get("DEBUG", "false").lower() == "true"
    )
```

### Migration Scripts

```python
# migrate_secrets.py
"""Script to migrate unencrypted secrets to secure-env."""

import os
from secure_env import Secrets

def migrate_from_env_file(source_file: str, target_file: str, master_key: str):
    """Migrate a .env file to secure-env."""
    
    print(f"🔄 Migrating {source_file} to {target_file}")
    
    # Initialize secure-env
    secrets = Secrets(master_key=master_key, env_file=target_file)
    
    # Read source file
    migrated_count = 0
    with open(source_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if '=' not in line:
                print(f"⚠️  Line {line_num}: Invalid format")
                continue
            
            key, value = line.split('=', 1)
            key = key.strip()
            
            # Clean quotes
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Determine if should encrypt
            sensitive_keywords = ['password', 'secret', 'key', 'token', 'api']
            should_encrypt = any(keyword in key.lower() for keyword in sensitive_keywords)
            
            # Migrate
            secrets.set(key, value, encrypt=should_encrypt)
            migrated_count += 1
            
            status = "🔒" if should_encrypt else "📄"
            print(f"  {key} {status}")
    
    print(f"✅ Migrated {migrated_count} variables")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python migrate_secrets.py <source.env> <target.env> <master_key>")
        sys.exit(1)
    
    source_file, target_file, master_key = sys.argv[1:4]
    migrate_from_env_file(source_file, target_file, master_key)
```

## 🔒 Security Guide

### Secure Key Generation

```python
from secure_env.utils import generate_random_key
import secrets
import base64

# Method 1: Use built-in utility
master_key = generate_random_key()
print(f"Generated key: {master_key}")

# Method 2: Manual generation
random_bytes = secrets.token_bytes(32)
manual_key = base64.urlsafe_b64encode(random_bytes).decode()
print(f"Manual key: {manual_key}")
```

### Secure Key Storage

```bash
# ❌ NEVER in source code
secrets = Secrets(master_key="hardcoded-key")

# ❌ NEVER in versioned config files
# config.py
MASTER_KEY = "exposed-key"

# ✅ System environment variable
export SECURE_ENV_MASTER_KEY="secure-key"

# ✅ Cloud secret managers (AWS Secrets Manager, Azure Key Vault)
# ✅ Hashicorp Vault
# ✅ Kubernetes Secrets

# ✅ Secure local file (development only)
echo "my-master-key" > ~/.secure-env-key
chmod 600 ~/.secure-env-key
export SECURE_ENV_MASTER_KEY=$(cat ~/.secure-env-key)
```

### Regular Key Rotation

```bash
#!/bin/bash
# rotate_keys.sh - Automatic rotation script

# Backup current state
secure-env export --format dotenv > backup-$(date +%Y%m%d).env

# Generate new key
NEW_KEY=$(python -c "from secure_env.utils import generate_random_key; print(generate_random_key())")

# Perform rotation
secure-env rotate-key --new-key "$NEW_KEY"

# Update systems
echo "🔄 Update SECURE_ENV_MASTER_KEY in all systems:"
echo "   New key: $NEW_KEY"

# Notify teams
echo "📧 Notify team members about key rotation"
```

### Audit and Monitoring

```python
# audit.py - Secrets audit script
from secure_env import Secrets
import datetime
import json

def audit_secrets(env_file: str):
    """Perform secrets audit."""
    
    secrets = Secrets(env_file=env_file)
    keys_info = secrets.list_keys()
    
    audit_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "env_file": env_file,
        "total_variables": len(keys_info),
        "encrypted_count": sum(1 for is_enc in keys_info.values() if is_enc),
        "plain_count": sum(1 for is_enc in keys_info.values() if not is_enc),
        "variables": {}
    }
    
    # Analyze each variable
    for key, is_encrypted in keys_info.items():
        audit_report["variables"][key] = {
            "encrypted": is_encrypted,
            "potential_secret": any(word in key.lower() for word in 
                                  ['password', 'secret', 'key', 'token', 'api'])
        }
    
    return audit_report

# Usage
report = audit_secrets(".env.production")
print(json.dumps(report, indent=2))
```

### Security Testing and Validation

```python
# security_tests.py
import unittest
from secure_env import Secrets
from secure_env.exceptions import DecryptionError

class SecurityTests(unittest.TestCase):
    
    def test_wrong_key_fails(self):
        """Verify wrong key fails."""
        secrets1 = Secrets(master_key="key1", env_file="test1.env")
        secrets1.set("TEST", "secret")
        
        secrets2 = Secrets(master_key="key2", env_file="test1.env")
        with self.assertRaises(DecryptionError):
            secrets2.get("TEST")
    
    def test_encrypted_at_rest(self):
        """Verify secrets are encrypted on disk."""
        secrets = Secrets(master_key="test-key", env_file="test2.env")
        secrets.set("PASSWORD", "secret123")
        
        # Read file directly
        with open("test2.env", 'r') as f:
            content = f.read()
        
        # Secret should not appear in plain text
        self.assertNotIn("secret123", content)
        self.assertIn("ENC(", content)
    
    def test_key_rotation(self):
        """Test key rotation."""
        secrets = Secrets(master_key="old-key", env_file="test3.env")
        secrets.set("TEST", "value")
        
        # Rotation
        secrets.change_master_key("new-key")
        
        # Verify value is still accessible
        self.assertEqual(secrets.get("TEST"), "value")
        
        # Verify old key can't decrypt anymore
        old_secrets = Secrets(master_key="old-key", env_file="test3.env")
        with self.assertRaises(DecryptionError):
            old_secrets.get("TEST")

if __name__ == '__main__':
    unittest.main()
```

## 🚀 Performance and Optimization

### Performance Benchmarks

```python
# benchmark.py
import time
from secure_env import Secrets

def benchmark_operations(num_operations: int = 1000):
    """Benchmark basic operations."""
    
    secrets = Secrets(master_key="benchmark-key", env_file="benchmark.env")
    
    # Test set (encryption)
    start = time.time()
    for i in range(num_operations):
        secrets.set(f"KEY_{i}", f"value_{i}")
    set_time = time.time() - start
    
    # Test get (decryption)
    start = time.time()
    for i in range(num_operations):
        _ = secrets.get(f"KEY_{i}")
    get_time = time.time() - start
    
    print(f"📊 Benchmark Results ({num_operations} operations):")
    print(f"   Set operations: {set_time:.2f}s ({num_operations/set_time:.1f} ops/sec)")
    print(f"   Get operations: {get_time:.2f}s ({num_operations/get_time:.1f} ops/sec)")
    
    # Cleanup
    import os
    os.remove("benchmark.env")

if __name__ == "__main__":
    benchmark_operations()
```

### Recommended Optimizations

```python
# Single initialization (recommended)
class AppConfig:
    _secrets = None
    
    @classmethod
    def get_secrets(cls):
        if cls._secrets is None:
            cls._secrets = Secrets()
        return cls._secrets

# Usage
config = AppConfig()
secrets = config.get_secrets()
db_password = secrets.get("DATABASE_PASSWORD")

# Cache frequently used values
class CachedSecrets:
    def __init__(self, master_key: str):
        self.secrets = Secrets(master_key=master_key)
        self._cache = {}
    
    def get(self, key: str, default=None):
        if key not in self._cache:
            self._cache[key] = self.secrets.get(key, default)
        return self._cache[key]
    
    def invalidate_cache(self):
        self._cache.clear()
```

## 🐛 Troubleshooting and FAQ

### Common Issues

#### 1. "InvalidKeyError: Master key is required"

```bash
# Cause: No master key provided
# Solutions:
export SECURE_ENV_MASTER_KEY='your-key'
# or
secure-env set KEY value --master-key 'your-key'
```

#### 2. "DecryptionError: Invalid encrypted data or wrong master key"

```bash
# Cause: Wrong key or corrupted data
# Diagnosis:
secure-env check

# Solutions:
# - Verify master key
# - Restore from backup
# - Re-encrypt with correct key
```

#### 3. "FileAccessError: Cannot read .env"

```bash
# Cause: Insufficient permissions
# Solution:
chmod 600 .env
chown $USER:$USER .env
```

#### 4. Variables not loaded in application

```python
# Problem: Variables not in os.environ
# Solution:
from secure_env import Secrets
secrets = Secrets()
secrets.export_to_os_environ()

# or in shell:
eval $(secure-env export --format env)
```

### FAQ

**Q: Can I use secure-env without CLI?**
A: Yes, the Python API works independently of the CLI.

```python
from secure_env import Secrets
secrets = Secrets(master_key="key")
secrets.set("VAR", "value")
```

**Q: How to share secrets between teams?**
A: Share the encrypted .env file + master key via separate secure channels.

**Q: What happens if I lose the master key?**
A: Encrypted secrets are permanently lost. Keep backups of the key!

**Q: Can I use multiple .env files?**
A: Yes, specify the file with `-f` or `env_file` parameter.

```bash
secure-env -f .env.production set API_KEY 'prod-key'
```

**Q: How to integrate with Docker Secrets?**
A: Mount the secret as environment variable:

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - SECURE_ENV_MASTER_KEY_FILE=/run/secrets/master_key
    secrets:
      - master_key
```

**Q: Performance with many variables?**
A: Secure-env is optimized for hundreds of variables. For more, use caching.

**Q: Kubernetes compatible?**
A: Yes, use ConfigMaps for .env and Secrets for master key.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secure-env-key
data:
  master-key: <base64-encoded-key>
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-env
data:
  .env: |
    API_KEY=ENC(gAAAAA...)
    DB_PASSWORD=ENC(gAAAAA...)
```

## 📈 Roadmap and Evolution

### Current Version (2.0.0)
- ✅ AES-256 encryption
- ✅ Complete CLI
- ✅ Python API
- ✅ Multi-file support
- ✅ Import/Export
- ✅ Key rotation

### Future Versions

#### v1.1.0 (Planned)
- 🔄 Shared keys support (team keys)
- 🔄 Cloud integration (AWS, Azure, GCP)
- 🔄 Automatic backup
- 🔄 Rotation webhooks

#### v1.2.0 (Under consideration)
- 🤔 Web management interface
- 🤔 RBAC support (Role-Based Access)
- 🤔 Complete audit trail
- 🤔 Plugin system

## 🤝 Contributing

### How to Contribute

1. **Fork** the repository
2. **Clone** your fork
3. **Create** a feature branch
4. **Code** with best practices
5. **Test** your changes
6. **Commit** and **push**
7. **Create** a Pull Request

```bash
# Development setup
git clone https://github.com/Moesthetics-code/secure-env.git
cd secure-env
pip install -e ".[dev]"

# Run tests
make test

# Check style
make lint format-check

# Local build
make build
```

### Contribution Standards

- **Tests** : Minimum 85% coverage
- **Style** : Black + flake8
- **Types** : Type hints required
- **Docs** : Docstrings + examples
- **Changelog** : Entry for each PR

### Areas Looking for Improvement

- 🔍 **Security** : Audits, vulnerabilities
- 🚀 **Performance** : Optimizations
- 📱 **UX** : CLI/API improvements
- 🔌 **Integrations** : New frameworks
- 📚 **Documentation** : Examples, guides

## 📞 Support and Community

### Support Channels

- **📧 Email**: support@secure-env.dev
- **🐛 Issues**: [GitHub Issues](https://github.com/Moesthetics-code/secure-env/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/Moesthetics-code/secure-env/discussions)
- **📚 Documentation**: [docs.secure-env.dev](https://docs.secure-env.dev)

### Community

- **⭐ GitHub**: Starred by X developers
- **📦 PyPI**: X downloads/month
- **🐦 Twitter**: [@secure_env](https://twitter.com/secure_env)
- **💼 LinkedIn**: [Secure-Env Community](https://linkedin.com/company/secure-env)

### Sponsoring

Secure-Env is an open source project. Support development:

- **☕ Buy me a coffee**: [buymeacoffee.com/secure-env](https://buymeacoffee.com/secure-env)
- **💚 GitHub Sponsors**: [GitHub Sponsors](https://github.com/sponsors/Moesthetics-code)
- **🏢 Enterprise Support**: Contact us for enterprise support

---

## 📄 License and Credits

### License
This project is licensed under **MIT License**. See [LICENSE](LICENSE) for details.

### Credits

- **Encryption**: [Cryptography](https://cryptography.io/) library
- **Inspiration**: Real-world production security problems
- **Community**: Contributors and users

### Acknowledgments

Thanks to all contributors, testers, and users who make this project possible!

---

**🔐 Secure-Env - Secure your secrets, simplify your life!**

*Made with ❤️ for the Python community*