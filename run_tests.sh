#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

VENV_DIR=".venv_tests"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in $VENV_DIR..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment $VENV_DIR already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update requirements
echo "Installing test requirements from test_requirements.txt..."
pip install -r test_requirements.txt

# Run the Python test script
echo "Running API tests with test_api.py..."
python3 test_api.py

# Deactivate the virtual environment
deactivate
echo "Tests finished."
