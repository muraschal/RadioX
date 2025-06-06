#!/bin/bash

# RadioX Environment Setup Script
# Vereinfachter Zugang zum Python Setup Manager

echo "🚀 RadioX Environment Setup"
echo ""

# Check if we're in the right directory
if [ ! -f "setup_env.py" ]; then
    echo "❌ Fehler: setup_env.py nicht gefunden!"
    echo "   Bitte führe dieses Script aus dem RadioX Root-Verzeichnis aus."
    exit 1
fi

# Run the Python setup script
python3 setup_env.py

echo ""
echo "💡 Für direkte Verwendung: python3 setup_env.py" 