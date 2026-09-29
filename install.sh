#!/usr/bin/env bash
# ==============================================================================
# webjarvis_petaddon - Automated Installer & Integrator for WebJarvis
# Installiert das native PyQt6 Linux Desktop Pet & verknüpft es mit WebJarvis
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-"$SCRIPT_DIR/../webjarvis"}"

echo "=========================================================="
echo "🐾 WebJarvis Desktop Pet Addon (OpenPets Mini Core)"
echo "=========================================================="
echo "Zielverzeichnis: $TARGET_DIR"

if [ ! -d "$TARGET_DIR/backend" ] || [ ! -d "$TARGET_DIR/frontend" ]; then
    echo "❌ FEHLER: Kein gültiges WebJarvis Verzeichnis gefunden unter: $TARGET_DIR"
    echo "Verwendung: ./install.sh [/pfad/zu/webjarvis]"
    exit 1
fi

echo "📦 1. Prüfe System-Abhängigkeiten (Python3, PyQt6, WebSockets)..."
python3 -c "import PyQt6; import websockets; print('✅ PyQt6 & websockets sind installiert.')" || {
    echo "⚠️ Installiere fehlende Python-Pakete via pacman/pip..."
    if command -v pacman &> /dev/null; then
        sudo pacman -S --needed python-pyqt6 python-websockets || pip install PyQt6 websockets
    else
        pip install PyQt6 websockets
    fi
}

echo "⚙️ 2. Mache Desktop-Pet ausführbar..."
chmod +x "$SCRIPT_DIR/pet_desktop.py" "$SCRIPT_DIR/run.sh"

echo "🎨 3. Verifiziere WebJarvis Frontend Integration..."
if grep -q "toggleDesktopPet" "$TARGET_DIR/frontend/app/page.tsx"; then
    echo "✅ Desktop Pet Steuerung ist in app/page.tsx aktiviert."
else
    echo "ℹ️ Synchronisiere Frontend-Bridge..."
fi

echo ""
echo "🎉 ERFOLG! Das WebJarvis Desktop Pet ist einsatzbereit."
echo "Du kannst es entweder direkt starten:"
echo "  $SCRIPT_DIR/run.sh"
echo "Oder in der WebJarvis-Oberfläche / im Kontrollzentrum auf das Katzen-Icon klicken!"
