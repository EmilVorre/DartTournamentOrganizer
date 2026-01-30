#!/bin/bash

# Build script for creating Mac .app bundle
# This script must be run on a Mac for the final .app bundle

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠ Warning: This script is designed for macOS."
    echo "   You're running on: $OSTYPE"
    echo "   The build will create a Linux executable instead of a .app bundle."
    echo "   For a Mac .app bundle, you must run this on a Mac."
    echo ""
fi

echo "Building Dart Tournament..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist __pycache__

# Build the application
echo "Building application..."
if [ -f "DartTournament.spec" ]; then
    echo "Using DartTournament.spec file..."
    pyinstaller DartTournament.spec
    BUILD_EXIT_CODE=$?
else
    echo "⚠ Spec file not found. Building directly from Python file..."
    echo "   (This will create a basic build. For best results, commit DartTournament.spec to git)"
    pyinstaller --name=DartTournament \
        --windowed \
        --onedir \
        --add-data "dartboard.png:." \
        --icon=Icons/icon.ico \
        --osx-bundle-identifier=com.darttournament.app \
        DartTournament.py
    BUILD_EXIT_CODE=$?
fi

# Check if pyinstaller failed
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "✗ Build failed with exit code $BUILD_EXIT_CODE"
    echo "  Check the output above for errors."
    exit 1
fi

# Check if build was successful
if [ -d "dist/DartTournament.app" ]; then
    echo ""
    echo "✓ Build successful!"
    echo "✓ Mac application created at: dist/DartTournament.app"
    echo ""
    echo "You can now distribute the DartTournament.app bundle."
    echo "Note: Users may need to right-click and select 'Open' the first time"
    echo "      due to macOS security restrictions (if not code-signed)."
elif [ -d "dist/DartTournament" ]; then
    echo ""
    echo "✓ Build successful (Linux executable)!"
    echo "✓ Application created at: dist/DartTournament/"
    echo ""
    echo "⚠ Note: This is a Linux build. For a Mac .app bundle,"
    echo "        you must run this script on a macOS system."
    echo ""
    echo "To run on Linux: ./dist/DartTournament/DartTournament"
else
    echo "✗ Build failed. Check the output above for errors."
    exit 1
fi
