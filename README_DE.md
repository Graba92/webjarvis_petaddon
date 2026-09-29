# 🐾 Desktop Pet & Tamagotchi AI Companion v2.5 (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

Ein interaktiver, animierter **vollständig eigenständiger Linux Desktop Companion** & **Tamagotchi**, inspiriert von **OpenPets**. Läuft direkt auf deinem Linux Desktop (KDE Plasma / CachyOS / X11 / Wayland) als rahmenloses, transparentes Always-on-Top Fenster mit OpenPets V2 Blickverfolgung, autonomem Umherwandern, 4 wählbaren Charakter-Stimmen, Tamagotchi-Bedürfnissystem und einer kleinen frechen **Nervensäge**, die dich an Pausen, Wassertrinken, Essen und Termine erinnert!

---

## ✨ Neue & Erweiterte Highlights (v2.5)

- **🖥️ 100% Standalone Desktop-Begleiter**: Läuft vollkommen unabhängig als native PyQt6-Anwendung direkt auf deinem Bildschirm – ohne Webbrowser oder externe Server.
- **🤖 Universelle KI-Anbindung (Egal welches LLM)**:
  - Voll konfigurierbar für **Google Gemini**, **OpenAI**, **Groq**, **OpenRouter**, **Ollama** oder jede benutzerdefinierte Base-URL.
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
- **🎾 Interaktives Ball-Fangspiel (Fetch Game)**:
  - Rechtsklick ➔ *🎾 Ball werfen (Fangspiel)*: Ein kleiner Tennisball hüpft physikalisch korrekt über deinen Desktop!
  - Yuyu rennt aufgeregt hinterher, fängt den Ball mit einem Freudensprung, spielt einen Fang-Sound ab und bringt ihn stolz zurück!
- **💤 Schlaf- & DND-Nachtmodus (Deep Sleep)**:
  - Rechtsklick ➔ *💤 Schlafen legen (Zzz... DND)*: Yuyu rollt sich friedlich zusammen, blaue `Zzz...`-Partikel steigen auf.
  - Im Schlafmodus sind alle Nervensägen-Alarme stummgeschaltet, damit du ungestört arbeiten kannst.
- **🍅 Pomodoro Fokus-Trainer (25m / 5m)**:
  - Integrierter Pomodoro-Timer im HUD. Yuyu feuert dich an und ruft nach 25 Minuten pünktlich zur 5-Minuten-Pause auf.
- **⭐ RPG Progression & Level-System**:
  - Sammle Erfahrungspunkte (XP) für jedes getrunkene Glas Wasser (+25 XP), Pausen (+35 XP), Snacks und Fangspiele!
  - Steige auf: *Neuling* ➔ *Bekannter* ➔ *Kumpel* ➔ *Guter Freund* ➔ *Bester Freund* ➔ *Seelenverwandter*!
- **🍽️ Snack-Bar (5 verschiedene Snacks)**:
  - 🥪 *Sandwich / Mahlzeit* (+50% Hunger)
  - 🍎 *Knackiger Apfel* (+25% Hunger, +10% Vitalität)
  - ☕ *Heißer Kaffee / Espresso* (+40% Energie-Boost)
  - 🥤 *Frisches Glas Wasser* (+50% Hydration)
  - 🍩 *Süßer Donut* (+30% Hunger, +10 Zuneigung)
- **🎵 Pure Python Retro-Soundeffekte (SFX)**:
  - Eingebauter Synthesizer (Happy Arpeggio, Level-Up Fanfare, Notstand-Alarm, Schlummerton, Pomodoro-Gong) ohne externe Libraries.
- **🎨 4 Wählbare HUD-Themes**:
  - 🔵 **Cyberpunk Neon** (Cyan & Dunkelblau)
  - 🟢 **Gameboy Retro** (Vintage Matrix-Grün)
  - 🌸 **Kawaii Pastel** (Sakura-Rosa & Flieder)
  - 🌙 **Minimal Slate** (Dezentes Schiefergrau & Silber)
- **📊 Health-Dashboard & Statistiken**:
  - Zählt getrunkene Gläser Wasser, Mahlzeiten, Pausen, Pomodoros und konsekutive Streak-Tage!
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
- **Konfiguration:** Rechtsklick auf das Pet ➔ *⚙️ Einstellungen & Dashboard...*

---

## ⚙️ Konfiguration

Alle Einstellungen werden automatisch in `~/.config/desktop_pet/config.json` gespeichert:
- API-Keys und Modellwahl
- Ausgewählte Stimme & Lautstärke
- Tamagotchi-Verfallszeiten & HUD-Theme
- RPG Level, Zuneigung & Tages-Statistiken
- Termine und Fensterposition

---

## 📜 Lizenz

MIT Lizenz. Entwickelt von Matthias Haase (Graba92) für die Valhalla Tools Suite.
