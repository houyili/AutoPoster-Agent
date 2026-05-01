#!/bin/bash
set -e

echo "========================================="
echo "  AutoPoster-Agent One-Click Installer"
echo "========================================="

# 1. Check Python version (require 3.8+)
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; }; then
    echo "❌ Error: Python 3.8+ is required (found $PY_VERSION)."
    exit 1
fi
echo "✅ Python $PY_VERSION detected."

# 2. Check LaTeX compiler
if command -v tectonic &> /dev/null; then
    echo "✅ tectonic LaTeX compiler found."
elif command -v pdflatex &> /dev/null; then
    echo "✅ pdflatex found (ensure beamerposter, tcolorbox packages are installed)."
else
    echo "⚠️  Warning: No LaTeX compiler found (tectonic or pdflatex)."
    echo "   Install via: brew install tectonic (macOS) or cargo install tectonic"
    echo "   Continuing anyway..."
fi

# 3. Create Virtual Environment
printf "\n📦 Creating Python virtual environment (.venv)...\n"
python3 -m venv .venv
source .venv/bin/activate

# 4. Install Dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed."

# 5. Optional Keychain Setup
printf "\n"
read -p "🔐 Set up your LLM API key now? (y/N): " setup_key
if [ "$setup_key" = "y" ] || [ "$setup_key" = "Y" ]; then
    python setup_keychain.py
else
    echo "⏭️  Skipping keychain setup. You can run 'python setup_keychain.py' later."
fi

printf "\n=========================================\n"
echo "✅ Installation Complete!"
echo ""
echo "  Activate:  source .venv/bin/activate"
echo "  Generate:  python agent_loop.py path/to/your/paper.tex"
echo "  Help:      python agent_loop.py --help"
echo "========================================="
