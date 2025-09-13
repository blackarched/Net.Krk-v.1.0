#!/bin/bash
# Setup script for net.krak desktop shortcuts

echo "Setting up net.krak desktop shortcuts..."

# Get the current directory
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Update desktop files with correct paths
sed -i "s|/workspace|$CURRENT_DIR|g" "$CURRENT_DIR/netkrak-start.desktop"
sed -i "s|/workspace|$CURRENT_DIR|g" "$CURRENT_DIR/netkrak-stop.desktop"

# Make scripts executable
chmod +x "$CURRENT_DIR/start_netkrak.sh"
chmod +x "$CURRENT_DIR/stop_netkrak.sh"
chmod +x "$CURRENT_DIR/setup_desktop.sh"

# Copy desktop files to user applications directory
if [ -d "$HOME/.local/share/applications" ]; then
    cp "$CURRENT_DIR/netkrak-start.desktop" "$HOME/.local/share/applications/"
    cp "$CURRENT_DIR/netkrak-stop.desktop" "$HOME/.local/share/applications/"
    echo "Desktop shortcuts installed to $HOME/.local/share/applications/"
else
    echo "Warning: $HOME/.local/share/applications/ does not exist"
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications/"
    echo "Desktop database updated"
fi

# Make desktop files executable
chmod +x "$HOME/.local/share/applications/netkrak-start.desktop" 2>/dev/null
chmod +x "$HOME/.local/share/applications/netkrak-stop.desktop" 2>/dev/null

echo "Setup complete! You can now find 'Start net.krak' and 'Stop net.krak' in your applications menu."
echo ""
echo "To start net.krak manually:"
echo "  $CURRENT_DIR/start_netkrak.sh"
echo ""
echo "To stop net.krak manually:"
echo "  $CURRENT_DIR/stop_netkrak.sh"