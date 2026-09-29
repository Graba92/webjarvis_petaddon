#!/usr/bin/env bash
# ==============================================================================
# WebJarvis Desktop Pet Launcher
# ==============================================================================

# XWayland erzwingen, damit Roaming und Drag & Drop unter KDE Plasma Wayland funktionieren
export QT_QPA_PLATFORM=xcb

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/pet_desktop.py" "$@"
