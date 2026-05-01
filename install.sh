#!/bin/bash
set -e

echo "========================================="
echo "AutoPoster-Agent One-Click Installer"
echo "========================================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

# 2. Check Tectonic
if ! command -v tectonic &> /dev/null; then
    echo "⚠️ Warning: tectonic LaTeX compiler is not installed."
    echo "Please install it via: brew install tectonic (macOS) or refer to their docs."
    echo "Continuing anyway..."
fi

# 3. Create Virtual Environment
echo "\n📦 Creating Python virtual environment (.venv)..."
python3 -m venv .venv
source .venv/bin/activate

# 4. Install Dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Setup Keychain
echo "\n🔐 Launching Secure Keychain Setup..."
python setup_keychain.py

echo "\n========================================="
echo "✅ Installation Complete!"
echo "To activate the environment in the future, run: source .venv/bin/activate"
echo "To generate a poster, run: python generate_poster.py outline.md"
echo "========================================="
