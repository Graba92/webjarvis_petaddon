# 🐾 WebJarvis Pet Addon (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

Ein interaktives, animiertes Companion-Addon für **WebJarvis**, inspiriert von **OpenPets**. Ausgestattet mit nativer Spritesheet-Rendering-Engine, OpenPets V2 Blickverfolgung (Gaze Tracking), autonomem Umherwandern (Roaming) und Live-WebSocket-Reaktivität auf Jarvis-Zustände.

---

## ✨ Hauptfunktionen

- **🎮 OpenPets V2 Atlas-Kompatibilität**: Unterstützt 8×11 Sprite-Atlanten (192×208 Pixel pro Frame) nach exaktem OpenPets Codex V2 Standard.
- **👁️ Mauszeiger-Blickverfolgung (Gaze Tracking)**: 16-Sektoren-Richtungsmatrix (Zeilen 9 & 10) – das Pet folgt neugierig dem Mauszeiger über den Bildschirm.
- **🚶 Autonomes Wandern (Roaming)**: Selbstständige Bewegung mit Richtungswechseln, sanften Pausen und Bildschirmrand-Kollisionsschutz.
- **🔄 Live J.A.R.V.I.S. Synchronisation**:
  - `THINKING` ➜ Denken / Analysieren (Zeile 8).
  - `SPEAKING` ➜ Winken & Sprechblasen-Ausgabe (Zeile 3).
  - `LISTENING` / `CONFIRM` ➜ Wartend / Aufmerksam (Zeile 6).
  - `ERROR` ➜ Besorgter Fehler-Ausdruck (Zeile 5).
  - `IDLE` ➜ Entspanntes Blinzeln & Neutral-Pose (Zeile 0).
- **💬 Interaktive Sprechblasen**: Gibt Jarvis-Antworten in Echtzeit oder eigene kleine Companion-Dialoge aus.
- **🖱️ Drag & Drop**: Kann per Mauszug an jeden beliebigen Ort auf dem Bildschirm verschoben werden.
- **💖 Taktile Interaktion**: Klick zum Streicheln / Freuen (`jumping`), Schnurren bei Zuwendung und synthetisierte WebAudio-Soundeffekte.
- **⚙️ Integriertes Settings-HUD**: Direkt am Pet aufrufbar (Skalierung 40%–120%, Wandern an/aus, Gaze an/aus, Sound an/aus, Dialoge an/aus).

---

## 🚀 Installation & Schnellstart

Um das Addon in WebJarvis zu integrieren:

```bash
cd /home/graba/Schreibtisch/ASGRAD/Valhalla/TOOLS/GRABAS_GITHUB/webjarvis_petaddon
./install.sh
```

Alternativ mit benutzerdefiniertem Pfad:
```bash
./install.sh /pfad/zu/webjarvis
```

Anschließend WebJarvis starten und im unteren Steuerungs-Dock auf das **🐾 Katzen-Icon** klicken, um Yuyu zu aktivieren!

---

## 📜 Lizenz

MIT Lizenz. Entwickelt für die Valhalla Tools Suite.
