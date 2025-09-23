#!/usr/bin/env python3
"""
Build script for BelArabyAI SDK.

This script helps build the package for distribution.
"""

import os
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main build function."""
    print("🚀 Building BelArabyAI SDK package...")

    # Change to SDK directory
    sdk_dir = Path(__file__).parent.parent
    os.chdir(sdk_dir)

    # Clean previous builds
    if not run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning previous builds"):
        return False

    # Install build dependencies
    if not run_command("pip install build twine", "Installing build dependencies"):
        return False

    # Build the package
    if not run_command("python -m build", "Building package"):
        return False

    # Check the package
    if not run_command("python -m twine check dist/*", "Checking package"):
        return False

    print("\n✅ Package built successfully!")
    print("📦 Built files:")

    # List built files
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")

    print("\n📋 Next steps:")
    print("1. Test the package: pip install dist/belaraby-ai-sdk-*.whl")
    print("2. Upload to PyPI: python -m twine upload dist/*")
    print("3. Upload to TestPyPI: python -m twine upload --repository testpypi dist/*")


if __name__ == "__main__":
    main()
