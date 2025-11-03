#!/bin/bash
# Build script for creating macOS .app bundle using PyInstaller

set -e

echo "🔨 Building Accudent Importer.app..."

# Check if pyinstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
rm -rf build dist

# Build the app
pyinstaller \
    --name "Accudent Importer" \
    --windowed \
    --onedir \
    --icon icon.icns \
    --add-data "README.md:." \
    --hidden-import openpyxl \
    --hidden-import reportlab \
    --hidden-import pypdf \
    --hidden-import Quartz \
    --hidden-import Foundation \
    --osx-bundle-identifier com.accudent.importer \
    accudent_app.py

echo ""
echo "✅ Build complete!"
echo "📦 App location: dist/Accudent Importer.app"
echo ""
echo "To install:"
echo "  cp -r \"dist/Accudent Importer.app\" /Applications/"
echo ""
echo "To run:"
echo "  open \"dist/Accudent Importer.app\""
