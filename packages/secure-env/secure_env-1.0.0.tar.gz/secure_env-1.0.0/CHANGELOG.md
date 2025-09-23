# =============================================================================
# CHANGELOG.md
# =============================================================================
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of secure-env
- AES-256 encryption for environment variables
- Support for .env file format with encrypted values
- Master key support via parameter or environment variable
- Simple API for get/set/delete operations
- Key listing with encryption status
- Export to os.environ functionality
- Master key rotation feature
- Comprehensive test suite
- Full documentation and examples
- Type hints for better IDE support
- Error handling with custom exceptions

### Features
- **Core functionality**: Encrypt/decrypt environment variables
- **File management**: Safe atomic writes with backup/restore
- **Key derivation**: PBKDF2-based key generation from master password
- **Multiple formats**: Support for different data types (string, int, float, bool)
- **Flexibility**: Optional encryption per variable
- **Integration**: Easy export to os.environ
- **Security**: Industry-standard cryptography practices

### Security
- AES-256-GCM encryption
- PBKDF2 key derivation with 100,000 iterations
- Secure random key generation
- Safe file operations with error recovery
- No plaintext exposure in memory dumps

## [Unreleased]

### Planned
- Command-line interface (CLI) tool
- Integration examples for popular frameworks
- Performance optimizations
- Additional key derivation methods
- Backup and restore functionality
- Key rotation automation