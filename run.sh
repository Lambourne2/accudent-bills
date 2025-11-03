#!/bin/bash
# Quick launcher script for Accudent Importer

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found."
    echo "Please run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Launch app
exec "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/accudent_app.py"
