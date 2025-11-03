#!/bin/bash
# Accudent Importer - Desktop Installer
# Creates a clickable desktop icon for easy launching

set -e

echo "📦 Installing Accudent Importer to Desktop..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create .app bundle on Desktop
APP_NAME="Accudent Importer.app"
DESKTOP="$HOME/Desktop"
APP_PATH="$DESKTOP/$APP_NAME"

# Remove old version if exists
if [ -d "$APP_PATH" ]; then
    echo "🗑️  Removing old version..."
    rm -rf "$APP_PATH"
fi

# Create app bundle structure
echo "📁 Creating application bundle..."
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create launcher script
cat > "$APP_PATH/Contents/MacOS/Accudent" << 'EOF'
#!/bin/bash
# Navigate to app directory
cd "$(dirname "$0")/../../.."
APP_DIR="$(pwd)"

# Find the actual code directory (go up from .app bundle)
CODE_DIR="$HOME/Code/accudent-bills"

# Launch the app
cd "$CODE_DIR"
./run.sh
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

# Try to create a simple icon from the logo
if [ -f "$SCRIPT_DIR/accudentlogo.png.png" ]; then
    echo "🎨 Adding icon..."
    # macOS will use the PNG as an icon even without .icns conversion
    cp "$SCRIPT_DIR/accudentlogo.png.png" "$APP_PATH/Contents/Resources/icon.png"
    
    # Try to convert to .icns if sips is available
    if command -v sips &> /dev/null; then
        sips -s format icns "$SCRIPT_DIR/accudentlogo.png.png" --out "$APP_PATH/Contents/Resources/icon.icns" 2>/dev/null || true
    fi
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Launch the app by double-clicking:"
echo "   'Accudent Importer' on your Desktop"
echo ""
