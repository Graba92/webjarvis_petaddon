# 🐾 Desktop Pet & Tamagotchi AI Companion (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

Ein interaktiver, animierter **vollständig eigenständiger Linux Desktop Companion** & **Tamagotchi**, inspiriert von **OpenPets**. Läuft direkt auf deinem Linux Desktop (KDE Plasma / CachyOS / X11 / Wayland) als rahmenloses, transparentes Always-on-Top Fenster mit OpenPets V2 Blickverfolgung, autonomem Umherwandern, 4 wählbaren Charakter-Stimmen, Tamagotchi-Bedürfnissystem und einer kleinen frechen **Nervensäge**, die dich an Pausen, Wassertrinken, Essen und Termine erinnert!

---

## ✨ Hauptfunktionen

- **🖥️ 100% Standalone Desktop-Begleiter**: Läuft vollkommen unabhängig als native PyQt6-Anwendung direkt auf deinem Bildschirm – ohne Webbrowser oder externe Server.
- **🤖 Beliebiges LLM über API-Key konfigurierbar**:
  - Unterstützt **Google Gemini**, **OpenAI**, **Groq**, **OpenRouter**, **Ollama** oder benutzerdefinierte Base-URLs.
  - Erkennt eingetragene API-Keys automatisch (`AIzaSy...`, `sk-...`, `gsk_...`).
  - **Offline-Garantie:** Funktioniert auch komplett ohne API-Key und ohne Internet mit über 40 handgeschriebenen witzigen deutschen Sprüchen!
- **🎙️ 4 Charakter-Stimmen zur freien Auswahl**:
  1. 👧 **Lola**: Weiblich, lebhaft, quirlig & frech (Pitch 1.28)
  2. 👦 **Buster**: Männlich, sarkastisch, dynamisch & direkt (Pitch 0.95)
  3. 🌸 **Mimi**: Weiblich, sanft, liebevoll & fürsorglich (Pitch 1.10)
  4. 🧔 **Klaus**: Männlich, trocken, brummig & tief (Pitch 0.78)
  - Umschaltbar per Rechtsklick-Menü oder im Einstellungsfenster inkl. Probe-Audiobutton.
- **🐾 Echtes Tamagotchi-System & Live-Statusleiste**:
  - Zeigt 3 vitale Fortschrittsbalken direkt über dem Kopf des Pets:
    - 🥪 **Hunger / Essen** (0 - 100%, sinkt kontinuierlich)
    - 💧 **Durst / Wasser** (0 - 100%, warnt vor Dehydration)
    - ⚡ **Energie / Bildschirmpause** (0 - 100%, schützt vor Übermüdung)
    - 📅 **Nächster Termin & Countdown**
  - **Farbcodierung:** Grün (>50%) ➔ Gelb (25-50%) ➔ Alarm-Rot (<25%).
- **😼 Die kleine Nervensäge (Nagging Companion)**:
  - Fällt einer deiner Werte unter 25%, gibt das Pet keine Ruhe mehr:
    - Es springt aufgeregt auf und ab.
    - Eine Comic-Sprechblase mit einem frechen Spruch erscheint.
    - Es spricht dich mit der gewählten Stimme laut an, damit du endlich aufstehst, Wasser trinkst oder Pause machst!
  - Wählbare Intensität: *Sanfte Erinnerung*, *Frecher Begleiter* oder *Extreme Nervensäge*.
- **🥪 Interaktive Pflege ("Füttern & Tränken")**:
  - Rechtsklick auf das Pet für sofortige Aktionen:
    - 🥪 *Snack / Mahlzeit gegessen* (+50% Hunger)
    - 💧 *Glas Wasser getrunken* (+50% Durst)
    - 🧘 *Pause gemacht & gestreckt* (+100% Energie)
- **📅 Integrierter Terminkalender & Erinnerungen**:
  - Eigene Termine mit Datum & Uhrzeit eintragen.
  - Das Pet alarmiert dich pünktlich mit Sprachausgabe und Sprechblase.
- **🎨 Kristallklares Rendering & Wayland-Kompatibilität**:
  - Bilineare Kantenglättung (`SmoothTransformation`) – keine Pixel-Treppen.
  - Erzwingt `QT_QPA_PLATFORM=xcb` (XWayland), wodurch freies Drag & Drop und Roaming unter KDE Plasma Wayland perfekt funktionieren.
- **👁️ 16-Sektoren Blickverfolgung**: Das Pet schaut dem Mauszeiger über den gesamten Desktop neugierig hinterher.
- **🚶 Autonomes Roaming**: Läuft selbstständig am unteren Bildschirmrand entlang.

---

## 🚀 Feste OS-Installation & Start

Führe das Installationsskript aus, um das Tool dauerhaft im Betriebssystem unter `~/.local/share/webjarvis_petaddon` zu installieren:

```bash
chmod +x install.sh
./install.sh
```

Nach der Installation:
- **Terminal-Befehl:** `desktop-pet` (oder `webjarvis-pet`)
- **KDE / CachyOS Startmenü:** Unter *Dienstprogramme / Utilities* als „Desktop Pet & Tamagotchi AI (Yuyu)“
- **Konfiguration:** Rechtsklick auf das Pet ➔ *⚙️ Einstellungen & KI-Konfiguration...*

---

## ⚙️ Konfiguration

Alle Einstellungen werden automatisch in `~/.config/desktop_pet/config.json` gespeichert:
- API-Keys und Modellwahl
- Ausgewählte Stimme & Lautstärke
- Tamagotchi-Verfallszeiten (Minuten bis Durst/Hunger/Pause)
- Nerv-Häufigkeit & Intensität
- Termine und Fensterposition

---

## 📜 Lizenz

MIT Lizenz. Entwickelt von Matthias Haase (Graba92) für die Valhalla Tools Suite.
