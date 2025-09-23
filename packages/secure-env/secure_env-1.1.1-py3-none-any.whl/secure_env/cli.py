# =============================================================================
# secure_env/cli.py
# =============================================================================
"""Command Line Interface for secure-env package."""

import os
import sys
import argparse
import getpass
from typing import Optional, List
import json

from .core import Secrets
from .exceptions import SecureEnvError, InvalidKeyError, DecryptionError
from .utils import generate_random_key


def get_master_key(args) -> str:
    """Get master key from various sources."""
    if args.master_key:
        return args.master_key
    
    # Try environment variable
    env_key = os.environ.get('SECURE_ENV_MASTER_KEY')
    if env_key:
        return env_key
    
    # Prompt user for key
    if args.no_prompt:
        raise InvalidKeyError("No master key provided and --no-prompt specified")
    
    return getpass.getpass("🔑 Enter master key: ")


def format_output(data, output_format: str = 'table'):
    """Format output in different formats."""
    if output_format == 'json':
        print(json.dumps(data, indent=2))
    elif output_format == 'table' and isinstance(data, dict):
        if not data:
            print("No variables found.")
            return
        
        # Calculate column widths
        max_key_len = max(len(str(k)) for k in data.keys())
        max_val_len = max(len(str(v)) for v in data.values())
        
        # Headers
        print(f"{'Key':<{max_key_len}} | {'Value/Status':<{max_val_len}}")
        print(f"{'-' * max_key_len}-+-{'-' * max_val_len}")
        
        # Rows
        for key, value in data.items():
            print(f"{key:<{max_key_len}} | {value}")
    else:
        print(data)


def cmd_init(args):
    """Initialize a new secure environment."""
    print("🔧 Initializing secure environment...")
    
    if os.path.exists(args.env_file) and not args.force:
        print(f"❌ File {args.env_file} already exists. Use --force to overwrite.")
        return 1
    
    try:
        if args.generate_key:
            master_key = generate_random_key()
            print(f"🔑 Generated master key: {master_key}")
            print("⚠️  IMPORTANT: Save this key securely! You'll need it to decrypt your secrets.")
        else:
            master_key = get_master_key(args)
        
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        print(f"✅ Initialized secure environment in {args.env_file}")
        
        if args.generate_key:
            print(f"\n💡 To use this environment, set:")
            print(f"   export SECURE_ENV_MASTER_KEY='{master_key}'")
            
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return 1
    
    return 0


def cmd_set(args):
    """Set a variable."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        # Get value
        if args.value is None:
            if args.no_prompt:
                print("❌ No value provided and --no-prompt specified")
                return 1
            value = getpass.getpass(f"🔒 Enter value for {args.key}: ")
        else:
            value = args.value
        
        # Set the variable
        encrypt = not args.no_encrypt
        secrets.set(args.key, value, encrypt=encrypt)
        
        status = "encrypted" if encrypt else "plain"
        print(f"✅ Set {args.key} ({status})")
        
    except Exception as e:
        print(f"❌ Failed to set variable: {e}")
        return 1
    
    return 0


def cmd_get(args):
    """Get a variable."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        value = secrets.get(args.key, default=None)
        if value is None:
            print(f"❌ Variable '{args.key}' not found")
            return 1
        
        if args.show_encrypted and secrets.get(args.key, auto_decrypt=False) != value:
            encrypted_value = secrets.get(args.key, auto_decrypt=False)
            print(f"🔒 {args.key} (encrypted): {encrypted_value}")
            print(f"🔓 {args.key} (decrypted): {value}")
        else:
            if args.quiet:
                print(value)
            else:
                print(f"{args.key}: {value}")
        
    except DecryptionError:
        print(f"❌ Failed to decrypt '{args.key}' - wrong master key?")
        return 1
    except Exception as e:
        print(f"❌ Failed to get variable: {e}")
        return 1
    
    return 0


def cmd_list(args):
    """List all variables."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        keys_info = secrets.list_keys(show_encrypted=True)
        
        if not keys_info:
            print("No variables found.")
            return 0
        
        if args.show_values:
            # Show keys with values
            data = {}
            for key, is_encrypted in keys_info.items():
                try:
                    value = secrets.get(key)
                    status = " 🔒" if is_encrypted else " 📄"
                    data[key + status] = value
                except DecryptionError:
                    data[key + " 🔒❌"] = "<decryption failed>"
        else:
            # Show only keys with encryption status
            data = {
                key: "🔒 encrypted" if is_encrypted else "📄 plain"
                for key, is_encrypted in keys_info.items()
            }
        
        format_output(data, args.format)
        
    except Exception as e:
        print(f"❌ Failed to list variables: {e}")
        return 1
    
    return 0


def cmd_delete(args):
    """Delete a variable."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        if not args.force:
            confirm = input(f"❓ Delete '{args.key}'? (y/N): ")
            if confirm.lower() not in ['y', 'yes']:
                print("❌ Cancelled")
                return 1
        
        if secrets.delete(args.key):
            print(f"✅ Deleted '{args.key}'")
        else:
            print(f"❌ Variable '{args.key}' not found")
            return 1
        
    except Exception as e:
        print(f"❌ Failed to delete variable: {e}")
        return 1
    
    return 0


def cmd_export(args):
    """Export variables to different formats."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        keys_info = secrets.list_keys(show_encrypted=True)
        
        if args.export_format == 'env':
            # Export as shell variables
            for key in keys_info:
                try:
                    value = secrets.get(key)
                    # Escape shell special characters
                    if ' ' in value or any(c in value for c in ['$', '"', "'", '\\', '`']):
                        value = f'"{value.replace(chr(34), chr(92) + chr(34))}"'
                    print(f"export {key}={value}")
                except DecryptionError:
                    if not args.skip_failed:
                        print(f"# ❌ Failed to decrypt {key}", file=sys.stderr)
        
        elif args.export_format == 'json':
            # Export as JSON
            data = {}
            for key in keys_info:
                try:
                    data[key] = secrets.get(key)
                except DecryptionError:
                    if not args.skip_failed:
                        data[key] = "<DECRYPTION_FAILED>"
            
            print(json.dumps(data, indent=2))
        
        elif args.export_format == 'dotenv':
            # Export as .env format (decrypted)
            for key in keys_info:
                try:
                    value = secrets.get(key)
                    # Quote if necessary
                    if ' ' in value or '#' in value:
                        value = f'"{value}"'
                    print(f"{key}={value}")
                except DecryptionError:
                    if not args.skip_failed:
                        print(f"# Failed to decrypt {key}")
        
    except Exception as e:
        print(f"❌ Failed to export: {e}")
        return 1
    
    return 0


def cmd_import(args):
    """Import variables from file."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        if not os.path.exists(args.import_file):
            print(f"❌ Import file '{args.import_file}' not found")
            return 1
        
        imported_count = 0
        skipped_count = 0
        
        with open(args.import_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' not in line:
                    print(f"⚠️  Skipping line {line_num}: Invalid format")
                    skipped_count += 1
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                
                # Remove quotes
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Check if already exists
                if key in secrets.list_keys() and not args.overwrite:
                    print(f"⚠️  Skipping {key}: already exists (use --overwrite)")
                    skipped_count += 1
                    continue
                
                # Import
                encrypt = not args.no_encrypt
                secrets.set(key, value, encrypt=encrypt)
                imported_count += 1
        
        print(f"✅ Imported {imported_count} variables")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} items")
        
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return 1
    
    return 0


def cmd_rotate_key(args):
    """Rotate master key."""
    try:
        print("🔄 Rotating master key...")
        
        # Get current key
        current_key = get_master_key(args)
        secrets = Secrets(master_key=current_key, env_file=args.env_file)
        
        # Get new key
        if args.new_key:
            new_key = args.new_key
        elif args.generate_new:
            new_key = generate_random_key()
            print(f"🔑 Generated new master key: {new_key}")
        else:
            new_key = getpass.getpass("🔑 Enter new master key: ")
        
        # Rotate
        secrets.change_master_key(new_key)
        print("✅ Master key rotated successfully!")
        
        if args.generate_new:
            print(f"\n💡 Update your environment:")
            print(f"   export SECURE_ENV_MASTER_KEY='{new_key}'")
        
    except Exception as e:
        print(f"❌ Failed to rotate key: {e}")
        return 1
    
    return 0


def cmd_check(args):
    """Check environment file integrity."""
    try:
        master_key = get_master_key(args)
        secrets = Secrets(master_key=master_key, env_file=args.env_file)
        
        keys_info = secrets.list_keys(show_encrypted=True)
        
        total_vars = len(keys_info)
        encrypted_vars = sum(1 for is_enc in keys_info.values() if is_enc)
        plain_vars = total_vars - encrypted_vars
        
        failed_vars = []
        
        print(f"🔍 Checking {args.env_file}...")
        print(f"📊 Total variables: {total_vars}")
        print(f"🔒 Encrypted: {encrypted_vars}")
        print(f"📄 Plain text: {plain_vars}")
        
        # Test decryption of encrypted variables
        for key, is_encrypted in keys_info.items():
            if is_encrypted:
                try:
                    secrets.get(key)
                except DecryptionError:
                    failed_vars.append(key)
        
        if failed_vars:
            print(f"\n❌ Failed to decrypt {len(failed_vars)} variables:")
            for var in failed_vars:
                print(f"   - {var}")
            return 1
        else:
            print("\n✅ All encrypted variables can be decrypted successfully!")
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return 1
    
    return 0


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='secure-env',
        description='Secure environment variables manager with AES encryption',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  secure-env init                          # Initialize new environment
  secure-env init --generate-key           # Generate random master key
  secure-env set DB_PASSWORD               # Set encrypted variable (prompt for value)
  secure-env set API_KEY mykey123          # Set encrypted variable with value
  secure-env set DEBUG true --no-encrypt   # Set plain text variable
  secure-env get DB_PASSWORD               # Get variable value
  secure-env list                          # List all variables
  secure-env list --show-values            # List with values
  secure-env delete OLD_VAR                # Delete variable
  secure-env export --format env           # Export as shell variables
  secure-env import variables.env          # Import from file
  secure-env rotate-key --generate-new     # Generate and rotate to new key
  secure-env check                         # Check file integrity

Environment Variables:
  SECURE_ENV_MASTER_KEY                    # Master key for encryption
        """
    )
    
    # Global options
    parser.add_argument(
        '--env-file', '-f',
        default='.env',
        help='Environment file path (default: .env)'
    )
    parser.add_argument(
        '--master-key', '-k',
        help='Master key for encryption (use SECURE_ENV_MASTER_KEY env var instead)'
    )
    parser.add_argument(
        '--no-prompt',
        action='store_true',
        help='Do not prompt for missing values'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet output'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.1.1'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize secure environment')
    init_parser.add_argument('--generate-key', action='store_true', help='Generate random master key')
    init_parser.add_argument('--force', action='store_true', help='Overwrite existing file')
    init_parser.set_defaults(func=cmd_init)
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set a variable')
    set_parser.add_argument('key', help='Variable name')
    set_parser.add_argument('value', nargs='?', help='Variable value (prompt if not provided)')
    set_parser.add_argument('--no-encrypt', action='store_true', help='Store as plain text')
    set_parser.set_defaults(func=cmd_set)
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a variable')
    get_parser.add_argument('key', help='Variable name')
    get_parser.add_argument('--show-encrypted', action='store_true', help='Show both encrypted and decrypted values')
    get_parser.set_defaults(func=cmd_get)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all variables')
    list_parser.add_argument('--show-values', action='store_true', help='Show variable values')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    list_parser.set_defaults(func=cmd_list)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a variable')
    delete_parser.add_argument('key', help='Variable name')
    delete_parser.add_argument('--force', action='store_true', help='Do not prompt for confirmation')
    delete_parser.set_defaults(func=cmd_delete)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export variables')
    export_parser.add_argument('--format', choices=['env', 'json', 'dotenv'], default='env', 
                              dest='export_format', help='Export format')
    export_parser.add_argument('--skip-failed', action='store_true', help='Skip variables that fail to decrypt')
    export_parser.set_defaults(func=cmd_export)
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import variables from file')
    import_parser.add_argument('import_file', help='File to import from')
    import_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing variables')
    import_parser.add_argument('--no-encrypt', action='store_true', help='Import as plain text')
    import_parser.set_defaults(func=cmd_import)
    
    # Rotate key command
    rotate_parser = subparsers.add_parser('rotate-key', help='Rotate master key')
    rotate_parser.add_argument('--new-key', help='New master key')
    rotate_parser.add_argument('--generate-new', action='store_true', help='Generate new random key')
    rotate_parser.set_defaults(func=cmd_rotate_key)
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check environment integrity')
    check_parser.set_defaults(func=cmd_check)
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        return 1
    except Exception as e:
        if not args.quiet:
            print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())