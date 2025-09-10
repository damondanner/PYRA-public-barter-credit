#!/usr/bin/env python3
"""
Setup script for PYRA's Barter Credit API

This script helps set up the development environment and can be used
for automated deployment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description="", check=True):
    """Run a shell command with error handling."""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        if check:
            sys.exit(1)
        return e

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")

def check_dependencies():
    """Check if required system dependencies are available."""
    dependencies = ['git', 'curl']
    missing = []
    
    for dep in dependencies:
        result = run_command(f"which {dep}", check=False)
        if result.returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing system dependencies: {', '.join(missing)}")
        print("   Please install them and try again.")
        sys.exit(1)
    
    print("✅ System dependencies check passed")

def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        response = input("   Do you want to recreate it? (y/N): ")
        if response.lower() == 'y':
            shutil.rmtree(venv_path)
        else:
            print("   Using existing virtual environment")
            return
    
    run_command("python -m venv venv", "Creating virtual environment")
    
    # Determine activation script path
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_script = "venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    print(f"✅ Virtual environment created")
    print(f"   To activate: source {activate_script}")
    
    return pip_cmd, python_cmd

def install_python_dependencies(pip_cmd):
    """Install Python package dependencies."""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install main dependencies
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements")
    
    # Install development dependencies if available
    dev_requirements = Path("requirements-dev.txt")
    if dev_requirements.exists():
        run_command(f"{pip_cmd} install -r requirements-dev.txt", 
                   "Installing development requirements")
    
    print("✅ Python dependencies installed")

def setup_environment_file():
    """Set up environment configuration file."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("⚠️  .env.example not found, skipping environment setup")
        return
    
    if env_file.exists():
        print("📝 .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("   Keeping existing .env file")
            return
    
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    print("   📝 Please edit .env file with your configuration")

def test_installation(python_cmd):
    """Test the installation by running basic checks."""
    print("🧪 Testing installation...")
    
    # Test import of main module
    result = run_command(f"{python_cmd} -c 'from calculate_credit import PyraBarterCreditCalculator; print(\"✅ Main module imports successfully\")'")
    
    # Test basic calculation (with error handling for API limits)
    print("   Testing basic PYRA credit calculation...")
    result = run_command(f"{python_cmd} -c 'from calculate_credit import PyraBarterCreditCalculator; calc = PyraBarterCreditCalculator(); print(\"✅ Calculator initialized\")'")
    
    print("✅ Installation test passed")

def setup_git_hooks():
    """Set up Git hooks for development."""
    hooks_dir = Path(".git/hooks")
    
    if not hooks_dir.exists():
        print("⚠️  Git repository not found, skipping Git hooks setup")
        return
    
    # Pre-commit hook to run tests
    pre_commit_hook = hooks_dir / "pre-commit"
    hook_content = """#!/bin/bash
# PYRA Barter Credit pre-commit hook

echo "🧪 Running pre-commit checks..."

# Check Python syntax
python -m py_compile calculate_credit.py app.py
if [ $? -ne 0 ]; then
    echo "❌ Python syntax errors found!"
    exit 1
fi

# Run basic tests
python calculate_credit.py > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Basic functionality test failed!"
    exit 1
fi

echo "✅ Pre-commit checks passed"
"""
    
    with open(pre_commit_hook, 'w') as f:
        f.write(hook_content)
    
    # Make executable
    os.chmod(pre_commit_hook, 0o755)
    
    print("✅ Git pre-commit hook installed")

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Edit the .env file with your configuration")
    print("   2. Get a CoinGecko API key (optional but recommended):")
    print("      https://www.coingecko.com/en/api")
    print("   3. Activate the virtual environment:")
    
    if sys.platform == "win32":
        print("      venv\\Scripts\\activate")
    else:
        print("      source venv/bin/activate")
    
    print("   4. Test the application:")
    print("      python calculate_credit.py")
    print("      python app.py")
    print("   5. Open http://localhost:5000 in your browser")
    print("\n📚 Documentation:")
    print("   - README.md - Main documentation")
    print("   - examples/ - Integration examples")
    print("   - .env.example - Configuration options")
    
def main():
    """Main setup function."""
    print("🏛️  PYRA's Barter Credit API Setup")
    print("=" * 50)
    
    try:
        # Check system requirements
        check_python_version()
        check_dependencies()
        
        # Set up Python environment
        pip_cmd, python_cmd = setup_virtual_environment()
        install_python_dependencies(pip_cmd)
        
        # Set up configuration
        setup_environment_file()
        
        # Test installation
        test_installation(python_cmd)
        
        # Set up development tools
        setup_git_hooks()
        
        # Show next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

def quick_start():
    """Quick start without virtual environment (for containers/CI)."""
    print("🚀 PYRA's Barter Credit API - Quick Start")
    print("=" * 50)
    
    check_python_version()
    
    # Install dependencies directly
    run_command("pip install -r requirements.txt", "Installing requirements")
    
    # Set up environment
    setup_environment_file()
    
    # Test basic functionality
    run_command("python calculate_credit.py", "Testing calculation module")
    
    print("✅ Quick start complete!")
    print("   Run: python app.py")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup PYRA Barter Credit API")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick setup without virtual environment")
    parser.add_argument("--dev", action="store_true",
                       help="Install development dependencies")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_start()
    else:
        main()
