#!/bin/bash

# PyPI Publishing Script for AI Audit SDK
# This script builds and publishes the Python SDK to PyPI

set -e

echo "🔍 Checking for virtual environment and required tools..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if build and twine are installed
python -c "import build" 2>/dev/null || {
    echo "❌ 'build' package not found. Installing..."
    pip install build
}

python -c "import twine" 2>/dev/null || {
    echo "❌ 'twine' package not found. Installing..."
    pip install twine
}

echo "✅ All required tools are available"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "🏗️  Building the package..."
python -m build

# Check the built package
echo "🔍 Checking the built package..."
python -m twine check dist/*

# Get the current version
VERSION=$(python -c "from ai_audit_sdk import __version__; print(__version__)")
echo "📦 Package version: $VERSION"

# Confirm before publishing
echo "🚀 Ready to publish to PyPI!"
echo "📋 Package contents:"
ls -la dist/

read -p "Do you want to proceed with publishing? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Publishing to PyPI..."
    
    # Check if .pypirc exists
    if [ -f ".pypirc" ]; then
        echo "🔑 Using .pypirc configuration for authentication"
        python -m twine upload --config-file .pypirc dist/*
    else
        echo "⚠️  No .pypirc found, twine will prompt for credentials"
        python -m twine upload dist/*
    fi
    
    echo "✅ Successfully published ai-audit-sdk v$VERSION to PyPI!"
    echo "🔗 View at: https://pypi.org/project/ai-audit-sdk/$VERSION/"
else
    echo "❌ Publishing cancelled"
    exit 1
fi
