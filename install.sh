#!/usr/bin/env bash
# ==============================================================================
# 🐾 WebJarvis Desktop Pet — OS Installer & Updater
# Installiert das native PyQt6 Desktop-Pet dauerhaft in:
# ~/.local/share/webjarvis_petaddon
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/share/webjarvis_petaddon"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"

echo "=========================================================="
echo "🐾 WebJarvis Desktop Pet — OS Installer & Updater"
echo "=========================================================="
echo "Zielverzeichnis: $TARGET_DIR"

# 1. Zielverzeichnisse vorbereiten
mkdir -p "$TARGET_DIR" "$BIN_DIR" "$APP_DIR"

# 2. Dateien kopieren / aktualisieren
echo "📦 1. Synchronisiere Dateien nach $TARGET_DIR..."
cp -rv "$SCRIPT_DIR/pet_desktop.py" "$TARGET_DIR/"
cp -rv "$SCRIPT_DIR/run.sh" "$TARGET_DIR/"
cp -rv "$SCRIPT_DIR/pets" "$TARGET_DIR/"
if [ -d "$SCRIPT_DIR/lib" ]; then
    cp -rv "$SCRIPT_DIR/lib" "$TARGET_DIR/"
fi
if [ -d "$SCRIPT_DIR/components" ]; then
    cp -rv "$SCRIPT_DIR/components" "$TARGET_DIR/"
fi

# Berechtigungen sicherstellen
chmod +x "$TARGET_DIR/pet_desktop.py" "$TARGET_DIR/run.sh"

# 3. CLI-Starter in ~/.local/bin anlegen
echo "⚡ 2. Erstelle CLI-Starter in $BIN_DIR/webjarvis-pet..."
cat << 'EOF' > "$BIN_DIR/webjarvis-pet"
#!/usr/bin/env bash
export QT_QPA_PLATFORM=xcb
exec python3 "${HOME}/.local/share/webjarvis_petaddon/pet_desktop.py" "$@"
EOF
chmod +x "$BIN_DIR/webjarvis-pet"

# 4. Desktop-Entry für KDE Plasma / CachyOS Anwendungsmenü erstellen
echo "🖥️ 3. Erstelle Desktop-Eintrag in $APP_DIR/webjarvis-pet.desktop..."
cat << EOF > "$APP_DIR/webjarvis-pet.desktop"
[Desktop Entry]
Name=WebJarvis Desktop Pet (Yuyu Chibi)
Comment=Interaktiver animierter Desktop Companion für WebJarvis
Exec=${HOME}/.local/bin/webjarvis-pet
Icon=preferences-desktop-emoticons
Terminal=false
Type=Application
Categories=Utility;Amusement;
Keywords=jarvis;pet;openpets;yuyu;companion;
StartupNotify=false
EOF

# 5. Optional im System-Pfad prüfen
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "ℹ️ Hinweis: Füge $HOME/.local/bin zu deiner PATH-Variable hinzu, um 'webjarvis-pet' überall aufzurufen."
fi

echo ""
echo "🎉 ERFOLGREICH INSTALLIERT / AKTUALISIERT!"
echo "Standort: $TARGET_DIR"
echo "Befehl:   webjarvis-pet (oder $BIN_DIR/webjarvis-pet)"
echo "Starter:  Im KDE Anwendungsmenü unter Dienstprogramme / Utilities"
echo "WebJarvis: Kann das Pet jederzeit über das Katzen-Icon im Dock oder Kontrollzentrum starten!"
