#!/bin/bash
# Build script for APKM Repackager macOS app

echo "==================================="
echo "APKM Repackager - Build macOS App"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist

# Build the app
echo ""
echo "Building macOS application..."
python3 setup.py py2app

# Check if build succeeded
if [ -d "dist/APKM Repackager.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Your app is located at: dist/APKM Repackager.app"
    echo ""
    echo "To run the app:"
    echo "  open 'dist/APKM Repackager.app'"
    echo ""
    echo "To create a DMG for distribution:"
    echo "  hdiutil create -volname 'APKM Repackager' -srcfolder 'dist/APKM Repackager.app' -ov -format UDZO APKM-Repackager.dmg"
else
    echo ""
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi
