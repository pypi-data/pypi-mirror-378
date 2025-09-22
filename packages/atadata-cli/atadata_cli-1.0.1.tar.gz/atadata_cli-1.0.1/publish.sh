#!/bin/bash

# AtaData CLI Publishing Script
# This script helps publish the package to PyPI

set -e  # Exit on any error

echo "🚀 AtaData CLI Publishing Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Please run this script from the package root directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected."
    echo "   It's recommended to activate your virtual environment first:"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
make clean

# Build the package
echo "📦 Building package..."
python -m build

# Check the package
echo "✅ Checking package..."
twine check dist/*

echo ""
echo "📋 Package built successfully!"
echo "Files created:"
ls -la dist/

echo ""
echo "🎯 Next steps:"
echo "1. Create PyPI account at https://pypi.org/"
echo "2. Create API token in account settings"
echo "3. Configure authentication:"
echo "   touch ~/.pypirc"
echo "   # Add your API token to ~/.pypirc"
echo ""
echo "4. Upload to PyPI:"
echo "   twine upload dist/*"
echo ""
echo "   Or test on Test PyPI first:"
echo "   twine upload --repository testpypi dist/*"
echo ""
echo "5. Test installation:"
echo "   pip install atadata-cli"
echo "   atadata --help"
echo ""
echo "📖 For detailed instructions, see PYPI_PUBLISHING_GUIDE.md"
