# 🐾 WebJarvis Desktop Pet (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

Ein interaktiver, animierter **nativer Linux Desktop Companion** für **WebJarvis**, inspiriert von **OpenPets**. Läuft direkt auf deinem Linux Desktop (KDE Plasma / CachyOS) als rahmenloses, transparentes Always-on-Top Fenster mit OpenPets V2 Blickverfolgung, autonomem Umherwandern, Live-Stimmenwechsel ohne Neustart und voller Sprachreaktivität.

---

## ✨ Hauptfunktionen

- **🖥️ Echter Desktop-Begleiter**: Läuft mit PyQt6 direkt auf deinem Bildschirm über allen Fenstern (`Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`), 100% transparent.
- **🎨 Kristallklares Rendering**: Kein Verpixeln mehr dank bilinearer Kantenglättung (`SmoothTransformation`) und Anti-Aliasing.
- **🎮 OpenPets V2 Atlas-Kompatibilität**: Unterstützt 8×11 Sprite-Atlanten (192×208 Pixel pro Frame) nach exaktem OpenPets Codex V2 Standard.
- **👁️ Desktop Mauszeiger-Blickverfolgung**: 16-Sektoren-Richtungsmatrix (Zeilen 9 & 10) – das Pet folgt neugierig dem echten Mauszeiger über den gesamten Desktop.
- **🚶 Autonomes Wandern (Roaming)**: Läuft selbstständig am unteren Bildschirmrand entlang und dreht an Monitorgrenzen automatisch um.
- **🎙️ Live Stimmenwechsel per Rechtsklick (Ohne Neustart!)**:
  - 👨 **Männlich (Puck / Standard)**
  - 👩 **Weiblich (Aoede / Sanft & Natürlich)**
  - Aktualisiert die Gemini Live Session nahtlos in Echtzeit.
- **⚡ Jarvis Schnellsteuerung per Rechtsklick**:
  - 🎤 Mikrofon stummschalten / aktivieren (Mute / Unmute)
  - ⏹️ Sprachausgabe sofort unterbrechen (Interrupt)
  - 🌐 WebJarvis Weboberfläche im Browser öffnen (`http://localhost:3000`)
- **🖱️ Interaktives Bewegen (Drag & Drop)**: Packe Yuyu und setze sie an jeden beliebigen Ort auf dem Bildschirm – WebJarvis bemerkt die Bewegung und reagiert per Sprache!
- **🎵 Audio-Reaktivität**: Bounced sanft im Rhythmus von Jarvis' Stimme bei Sprachausgabe.
- **🔄 Live J.A.R.V.I.S. Synchronisation (ws://127.0.0.1:8765)**:
  - `THINKING` ➜ Denken / Analysieren (Zeile 8).
  - `SPEAKING` ➜ Winken & Sprechblasen-Ausgabe direkt über dem Pet auf dem Desktop.
  - `LISTENING` / `CONFIRM` ➜ Wartend / Aufmerksam (Zeile 6).
  - `ERROR` ➜ Besorgter Fehler-Ausdruck (Zeile 5).
  - `IDLE` ➜ Entspanntes Blinzeln & Neutral-Pose (Zeile 0).

---

## 🚀 Feste OS-Installation & Start

Führe das Installationsskript aus, um das Addon dauerhaft im Betriebssystem unter `~/.local/share/webjarvis_petaddon` zu installieren:

```bash
chmod +x install.sh
./install.sh
```

Nach der Installation:
- **Terminal-Befehl:** `webjarvis-pet`
- **KDE Anwendungsmenü:** Unter Dienstprogramme / Utilities als „WebJarvis Desktop Pet“
- **Aus WebJarvis:** Klick auf das **🐾 Katzen-Icon** im Bottom-Dock oder im Hardware-Kontrollzentrum!

---

## 📜 Lizenz

MIT Lizenz. Entwickelt von Matthias Haase (Graba92) für die Valhalla Tools Suite.
