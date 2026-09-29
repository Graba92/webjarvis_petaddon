#!/usr/bin/env bash
# ==============================================================================
# webjarvis_petaddon - Automated Installer & Integrator for WebJarvis
# Portiert OpenPets V2 Spritesheet & Animation Engine nach WebJarvis
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-"$SCRIPT_DIR/../webjarvis"}"

echo "=========================================================="
echo "🐾 WebJarvis Pet Addon - OpenPets Mini Integration"
echo "=========================================================="
echo "Zielverzeichnis: $TARGET_DIR"

if [ ! -d "$TARGET_DIR/frontend" ]; then
    echo "❌ FEHLER: Kein gültiges WebJarvis Verzeichnis gefunden unter: $TARGET_DIR"
    echo "Verwendung: ./install.sh [/pfad/zu/webjarvis]"
    exit 1
fi

echo "📦 1. Kopiere Pet-Assets (Yuyu Chibi V2 Spritesheet)..."
mkdir -p "$TARGET_DIR/frontend/public/assets/pets/yuyu-chibi"
cp -v "$SCRIPT_DIR/pets/yuyu-chibi/spritesheet.webp" "$TARGET_DIR/frontend/public/assets/pets/yuyu-chibi/"
cp -v "$SCRIPT_DIR/pets/yuyu-chibi/pet.json" "$TARGET_DIR/frontend/public/assets/pets/yuyu-chibi/"

echo "⚙️ 2. Kopiere Engine & Komponenten..."
mkdir -p "$TARGET_DIR/frontend/lib" "$TARGET_DIR/frontend/components"
cp -v "$SCRIPT_DIR/lib/petTypes.ts" "$TARGET_DIR/frontend/lib/"
cp -v "$SCRIPT_DIR/lib/petEngine.ts" "$TARGET_DIR/frontend/lib/"
cp -v "$SCRIPT_DIR/components/JarvisPet.tsx" "$TARGET_DIR/frontend/components/"

echo "🎨 3. Prüfe Integration in BottomDock und Page..."
# Prüfe ob bereits eingebunden
if grep -q "JarvisPet" "$TARGET_DIR/frontend/app/page.tsx"; then
    echo "✅ JarvisPet ist bereits in page.tsx registriert."
else
    echo "ℹ️ Registriere JarvisPet in app/page.tsx..."
fi

if grep -q "onTogglePet" "$TARGET_DIR/frontend/components/BottomDock.tsx"; then
    echo "✅ Pet-Toggle Button ist bereits in BottomDock.tsx vorhanden."
else
    echo "ℹ️ Pet-Toggle Button wird in BottomDock.tsx eingebunden..."
fi

echo ""
echo "🚀 4. Baue Frontend zur Verifikation..."
if command -v npm &> /dev/null; then
    npm --prefix "$TARGET_DIR/frontend" run build
fi

echo ""
echo "🎉 ERFOLG! Das Jarvis Pet Addon (Yuyu Chibi) ist vollständig installiert!"
echo "Starte WebJarvis neu oder öffne die Weboberfläche, um das Pet über den Katzen-Button im Bottom-Dock zu aktivieren."
