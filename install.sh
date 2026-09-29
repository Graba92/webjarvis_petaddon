#!/usr/bin/env bash
# ==============================================================================
# 🐾 Desktop Pet & Tamagotchi AI Companion — OS Installer & Updater
# Installiert das native PyQt6 Desktop-Pet dauerhaft in:
# ~/.local/share/webjarvis_petaddon
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/share/webjarvis_petaddon"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"

echo "=========================================================="
echo "🐾 Desktop Pet & Tamagotchi AI Companion — OS Installer"
echo "=========================================================="
echo "Zielverzeichnis: $TARGET_DIR"

# 1. Zielverzeichnisse vorbereiten
mkdir -p "$TARGET_DIR" "$BIN_DIR" "$APP_DIR"

# 2. Dateien kopieren / aktualisieren
echo "📦 1. Synchronisiere Dateien nach $TARGET_DIR..."
cp -rv "$SCRIPT_DIR/pet_desktop.py" "$TARGET_DIR/"
cp -rv "$SCRIPT_DIR/run.sh" "$TARGET_DIR/"
cp -rv "$SCRIPT_DIR/catalog_downloader.py" "$TARGET_DIR/"
cp -rv "$SCRIPT_DIR/pets" "$TARGET_DIR/"

# Berechtigungen sicherstellen
chmod +x "$TARGET_DIR/pet_desktop.py" "$TARGET_DIR/run.sh"

# 3. CLI-Starter in ~/.local/bin anlegen (desktop-pet und webjarvis-pet)
echo "⚡ 2. Erstelle CLI-Starter in $BIN_DIR/desktop-pet..."
cat << 'EOF' > "$BIN_DIR/desktop-pet"
#!/usr/bin/env bash
export QT_QPA_PLATFORM=xcb
exec python3 "${HOME}/.local/share/webjarvis_petaddon/pet_desktop.py" "$@"
EOF
chmod +x "$BIN_DIR/desktop-pet"

# Symlink / Alias für webjarvis-pet
ln -sf "$BIN_DIR/desktop-pet" "$BIN_DIR/webjarvis-pet"

# 4. Desktop-Entry für KDE Plasma / CachyOS Anwendungsmenü erstellen
echo "🖥️ 3. Erstelle Desktop-Eintrag in $APP_DIR/desktop-pet.desktop..."
cat << EOF > "$APP_DIR/desktop-pet.desktop"
[Desktop Entry]
Name=Desktop Pet & Tamagotchi AI (Yuyu)
Comment=Frecher animierter Desktop-Begleiter mit Tamagotchi-System, 4 Stimmen und Terminerinnerung
Exec=${HOME}/.local/bin/desktop-pet
Icon=preferences-desktop-emoticons
Terminal=false
Type=Application
Categories=Utility;Amusement;
Keywords=pet;tamagotchi;companion;ai;reminder;yuyu;openpets;
StartupNotify=false
EOF

# 5. Optional im System-Pfad prüfen
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "ℹ️ Hinweis: Füge $HOME/.local/bin zu deiner PATH-Variable hinzu, um 'desktop-pet' überall aufzurufen."
fi

echo ""
echo "🎉 ERFOLGREICH INSTALLIERT / AKTUALISIERT!"
echo "Standort: $TARGET_DIR"
echo "Befehl:   desktop-pet (oder webjarvis-pet)"
echo "Starter:  Im KDE Anwendungsmenü unter Dienstprogramme / Utilities"
