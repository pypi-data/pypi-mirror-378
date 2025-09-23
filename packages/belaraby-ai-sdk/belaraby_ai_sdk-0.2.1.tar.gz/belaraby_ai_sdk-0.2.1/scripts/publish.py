#!/usr/bin/env python3
"""
Publish script for BelArabyAI SDK.

This script helps publish the package to PyPI.
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
    """Main publish function."""
    print("🚀 Publishing BelArabyAI SDK package...")

    # Change to SDK directory
    sdk_dir = Path(__file__).parent.parent
    os.chdir(sdk_dir)

    # Check if dist directory exists
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ No dist directory found. Please run build.py first.")
        return False

    # Check if files exist
    dist_files = list(dist_dir.glob("*"))
    if not dist_files:
        print("❌ No files found in dist directory. Please run build.py first.")
        return False

    print("📦 Found files to upload:")
    for file in dist_files:
        print(f"  - {file.name}")

    # Ask for confirmation
    response = input("\n🤔 Do you want to upload to PyPI? (y/N): ")
    if response.lower() != "y":
        print("❌ Upload cancelled.")
        return False

    # Upload to PyPI
    if not run_command("python -m twine upload dist/*", "Uploading to PyPI"):
        return False

    print("\n✅ Package published successfully!")
    print("🎉 Your package is now available on PyPI!")
    print("📦 Install with: pip install belaraby-ai-sdk")


if __name__ == "__main__":
    main()
