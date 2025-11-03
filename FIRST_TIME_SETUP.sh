#!/bin/bash
# Accudent Importer - Complete First-Time Setup
# This script installs everything you need from scratch

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     🦷  ACCUDENT IMPORTER - FIRST TIME SETUP  🦷           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "This will install everything needed to run Accudent Importer."
echo "Estimated time: 5-10 minutes"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 Installing from: $SCRIPT_DIR"
echo ""

# Step 1: Check for Homebrew
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/5: Checking for Homebrew (macOS package manager)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew not found. Installing..."
    echo "⏳ This may take 5-10 minutes..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    echo "✅ Homebrew installed!"
else
    echo "✅ Homebrew already installed"
fi
echo ""

# Step 2: Install Python 3.12
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/5: Installing Python 3.12..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v python3.12 &> /dev/null; then
    echo "⏳ Installing Python 3.12 with tkinter support..."
    brew install python@3.12 python-tk@3.12
    echo "✅ Python 3.12 installed!"
else
    echo "✅ Python 3.12 already installed"
fi
echo ""

# Step 3: Create virtual environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/5: Setting up Python virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "venv" ]; then
    echo "ℹ️  Removing old virtual environment..."
    rm -rf venv
fi

# Try python3.12 first, fall back to python3
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "❌ Error: Python not found. Please install Python 3.12"
    exit 1
fi

echo "⏳ Creating virtual environment..."
$PYTHON_CMD -m venv venv
echo "✅ Virtual environment created!"
echo ""

# Step 4: Install dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/5: Installing Python packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "⏳ Installing dependencies (this may take a minute)..."
./venv/bin/pip install --upgrade pip > /dev/null
./venv/bin/pip install -r requirements.txt
echo "✅ Dependencies installed!"
echo ""

# Step 5: Create desktop launcher
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5/5: Creating desktop icon..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create logs directory
mkdir -p logs

APP_NAME="Accudent Importer.app"
DESKTOP="$HOME/Desktop"
APP_PATH="$DESKTOP/$APP_NAME"

# Remove old version if exists
if [ -d "$APP_PATH" ]; then
    rm -rf "$APP_PATH"
fi

# Create app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create launcher script that references THIS installation
cat > "$APP_PATH/Contents/MacOS/Accudent" << EOF
#!/bin/bash
# Accudent Importer Launcher
# Installation directory: $SCRIPT_DIR

cd "$SCRIPT_DIR"

# Find Python in virtual environment
if [ -f "./venv/bin/python3.12" ]; then
    PYTHON_BIN="./venv/bin/python3.12"
elif [ -f "./venv/bin/python3" ]; then
    PYTHON_BIN="./venv/bin/python3"
else
    osascript -e 'display dialog "Error: Python virtual environment not found. Please run FIRST_TIME_SETUP.sh again." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Launch the app
\$PYTHON_BIN accudent_app.py 2>&1 | tee logs/app.log
EOF

chmod +x "$APP_PATH/Contents/MacOS/Accudent"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Accudent</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleName</key>
    <string>Accudent Importer</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
EOF

# Add icon if available
if [ -f "accudentlogo.png.png" ]; then
    cp "accudentlogo.png.png" "$APP_PATH/Contents/Resources/icon.png"
    if command -v sips &> /dev/null; then
        sips -s format icns "accudentlogo.png.png" --out "$APP_PATH/Contents/Resources/icon.icns" 2>/dev/null || true
    fi
fi

echo "✅ Desktop icon created!"
echo ""

# Final message
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║               ✅  SETUP COMPLETE!  ✅                       ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Accudent Importer is ready to use!"
echo ""
echo "📍 Installation location: $SCRIPT_DIR"
echo ""
echo "🚀 TO LAUNCH:"
echo "   1. Find 'Accudent Importer' on your Desktop"
echo "   2. RIGHT-CLICK the icon"
echo "   3. Select 'Open'"
echo "   4. Click 'Open' again to confirm"
echo "   5. (After first time, you can just double-click)"
echo ""
echo "📖 For instructions, see: INSTRUCTIONS_FOR_USER.md"
echo ""
