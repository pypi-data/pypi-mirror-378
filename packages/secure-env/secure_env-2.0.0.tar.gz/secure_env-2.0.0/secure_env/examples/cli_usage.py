# =============================================================================
# examples/cli_usage.py
# =============================================================================
"""Examples of CLI usage for secure-env."""

import os
import subprocess
import tempfile

def run_command(cmd):
    """Run a CLI command and return output."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result

def demo_cli_usage():
    """Demonstrate CLI usage with examples."""
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        print("🚀 Secure-Env CLI Demo")
        print("=" * 50)
        
        # Set master key for demo
        os.environ['SECURE_ENV_MASTER_KEY'] = 'demo-key-123'
        
        # 1. Initialize
        print("\n1️⃣ Initialize secure environment:")
        run_command("secure-env init")
        
        # 2. Set variables
        print("\n2️⃣ Set encrypted variables:")
        run_command("secure-env set DB_PASSWORD 'super-secret-password'")
        run_command("secure-env set API_KEY 'sk-1234567890abcdef'")
        
        # 3. Set plain variable
        print("\n3️⃣ Set plain text variable:")
        run_command("secure-env set DEBUG true --no-encrypt")
        
        # 4. List variables
        print("\n4️⃣ List all variables:")
        run_command("secure-env list")
        
        # 5. Get specific variable
        print("\n5️⃣ Get specific variable:")
        run_command("secure-env get DB_PASSWORD")
        
        # 6. Show .env file content
        print("\n6️⃣ Current .env file content:")
        run_command("cat .env")
        
        # 7. Export variables
        print("\n7️⃣ Export as shell variables:")
        run_command("secure-env export --format env")
        
        # 8. Check integrity
        print("\n8️⃣ Check integrity:")
        run_command("secure-env check")
        
        print("\n✅ CLI Demo completed!")

if __name__ == "__main__":
    demo_cli_usage()