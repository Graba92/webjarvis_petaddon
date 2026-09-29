#!/usr/bin/env bash
# ==============================================================================
# webjarvis_petaddon - Uninstaller
# Entfernt das Pet-Addon aus WebJarvis
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-"$SCRIPT_DIR/../webjarvis"}"

echo "🐾 Entferne WebJarvis Pet Addon aus $TARGET_DIR..."

if [ -d "$TARGET_DIR/frontend/public/assets/pets/yuyu-chibi" ]; then
    rm -rf "$TARGET_DIR/frontend/public/assets/pets/yuyu-chibi"
    echo "✅ Pet-Assets entfernt."
fi

if [ -f "$TARGET_DIR/frontend/components/JarvisPet.tsx" ]; then
    rm -f "$TARGET_DIR/frontend/components/JarvisPet.tsx"
    echo "✅ JarvisPet.tsx entfernt."
fi

echo "Fertig. Falls gewünscht, passe app/page.tsx und BottomDock.tsx an."
