# 🐾 WebJarvis Desktop Pet (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

Ein interaktiver, animierter **nativer Linux Desktop Companion** für **WebJarvis**, inspiriert von **OpenPets**. Läuft direkt auf deinem Linux Desktop (KDE Plasma / CachyOS) als rahmenloses, transparentes Always-on-Top Fenster mit OpenPets V2 Blickverfolgung, autonomem Umherwandern und Live-WebSocket-Reaktivität auf Jarvis-Zustände.

---

## ✨ Hauptfunktionen

- **🖥️ Echter Desktop-Begleiter**: Läuft mit PyQt6 direkt auf deinem Bildschirm über allen Fenstern (`Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`), 100% transparent.
- **🎮 OpenPets V2 Atlas-Kompatibilität**: Unterstützt 8×11 Sprite-Atlanten (192×208 Pixel pro Frame) nach exaktem OpenPets Codex V2 Standard.
- **👁️ Desktop Mauszeiger-Blickverfolgung**: 16-Sektoren-Richtungsmatrix (Zeilen 9 & 10) – das Pet folgt neugierig dem echten Mauszeiger über den gesamten Desktop.
- **🚶 Autonomes Wandern (Roaming)**: Läuft selbstständig am unteren Bildschirmrand entlang und dreht an Monitorgrenzen automatisch um.
- **🎙️ Stimmenauswahl per Rechtsklick**: Einfach mit der rechten Maustaste auf das Pet auf dem Desktop klicken, um die Jarvis-Stimme umzustellen:
  - 👨 **Männlich (Puck / Standard)**
  - 👩 **Weiblich (Aoede / Sanft & Natürlich)**
- **🔄 Live J.A.R.V.I.S. Synchronisation (ws://127.0.0.1:8765)**:
  - `THINKING` ➜ Denken / Analysieren (Zeile 8).
  - `SPEAKING` ➜ Winken & Sprechblasen-Ausgabe mit Jarvis-Antworten direkt über dem Pet auf dem Desktop.
  - `LISTENING` / `CONFIRM` ➜ Wartend / Aufmerksam (Zeile 6).
  - `ERROR` ➜ Besorgter Fehler-Ausdruck (Zeile 5).
  - `IDLE` ➜ Entspanntes Blinzeln & Neutral-Pose (Zeile 0).
- **🖱️ Drag & Drop**: Mit linker Maustaste packen und frei auf dem Bildschirm verschieben.
- **⚡ 1-Klick Start aus WebJarvis**: Kann jederzeit über das **🐾 Katzen-Icon** im Bottom-Dock oder im Hardware-Kontrollzentrum von WebJarvis ein- und ausgeschaltet werden.

---

## 🚀 Schnellstart

Direkt über das Terminal starten:
```bash
./run.sh
```

Oder in WebJarvis auf den Pet-Button im Dock / Kontrollzentrum klicken!

---

## 📜 Lizenz

MIT Lizenz. Entwickelt von Matthias Haase (Graba92) für die Valhalla Tools Suite.
