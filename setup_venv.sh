#!/bin/bash

# Setup script for creating a virtual environment and installing dependencies
# Works on Linux (including Arch) and macOS

echo "Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
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
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "To activate the virtual environment in the future, run:"
    echo "  source venv/bin/activate"
    echo ""
    echo "To run the application:"
    echo "  source venv/bin/activate"
    echo "  python3 DartTournament.py"
else
    echo "✗ requirements.txt not found!"
    exit 1
fi
