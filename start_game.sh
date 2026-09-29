#!/usr/bin/env bash
# ==============================================================================
# 🐾 Yuyu Tamagotchi Life — One-Click Game Launcher
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/web_game"

echo "=========================================================="
echo "🐾 Starte Yuyus Tamagotchi Apartment & Händler Web-Game..."
echo "=========================================================="

python3 server.py "$@"
