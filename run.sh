#!/usr/bin/env bash
# ==============================================================================
# WebJarvis Desktop Pet Launcher
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/pet_desktop.py" "$@"
