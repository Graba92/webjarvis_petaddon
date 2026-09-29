# 🐾 Desktop Pet & Tamagotchi AI Companion v2.5 (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

Ein interaktiver, animierter **vollständig eigenständiger Linux Desktop Companion** & **Tamagotchi**, inspiriert von **OpenPets**. Läuft direkt auf deinem Linux Desktop (KDE Plasma / CachyOS / X11 / Wayland) als rahmenloses, transparentes Always-on-Top Fenster mit OpenPets V2 Blickverfolgung, autonomem Umherwandern, 4 wählbaren Charakter-Stimmen, Tamagotchi-Bedürfnissystem und einer kleinen frechen **Nervensäge**, die dich an Pausen, Wassertrinken, Essen und Termine erinnert!

---

## ✨ Neue & Erweiterte Highlights (v2.6)

- **🖥️ 100% Standalone Desktop-Begleiter**: Läuft vollkommen unabhängig als native PyQt6-Anwendung direkt auf deinem Bildschirm – ohne Webbrowser oder externe Server.
- **💖 Interaktives Streicheln & Schnurren**:
  - Doppelklick auf das Pet oder Rechtsklick ➔ *💖 Streicheln & Kraulen*: Yuyu schnurrt (`purr.wav`), tanzt vor Freude und eine Kaskade aus Herzen steigt auf (+15 XP, +10 Zuneigung).
- **🎮 Minispiele & Fun**:
  - 🎾 **Ball werfen (Fangspiel)**: Der Ball springt physikalisch korrekt über den Desktop, Yuyu jagt hinterher und fängt ihn.
  - 🎲 **Würfelspiel (1-6)**: Yuyu wirft mit Soundeffekt die Würfel und kommentiert das Ergebnis humorvoll.
  - 🥠 **Entwickler-Glückskeks**: Magischer Chime mit inspirierenden und witzigen Programmierer-Weisheiten.
- **🎭 Multi-Skin Manager & Skin-Wechsler**:
  - Unterstützt beliebig viele Pet-Skins (einfach Ordner in `pets/` oder `~/.local/share/webjarvis_petaddon/pets/` ablegen).
  - Umschalten direkt über das Rechtsklickmenü ohne Neustart.
  - Terminal-Befehl: `desktop-pet --skins`.
- **🧘 Ergonomie- & Haltungs-Coach**:
  - Rechtsklick ➔ *👁️ Ergonomie- & Haltungs-Check*: Erinnert an die 20-20-20-Augenregel und lockere Schultern.
- **💻 Hardware- & CPU-Last Wächter**:
  - Erkennt hohe Systemauslastung (Compile-Jobs, Rendering) und reagiert humorvoll mit Schweiß-Tropfen (`💦`) und Lüfter-Beistand.
- **🤖 Universelle KI-Anbindung (Egal welches LLM)**:
  - Voll konfigurierbar für **Google Gemini**, **OpenAI**, **Groq**, **OpenRouter**, **Ollama** oder jede benutzerdefinierte Base-URL.
  - Erkennt eingetragene API-Keys automatisch (`AIzaSy...`, `sk-...`, `gsk_...`).
  - **Offline-Garantie:** Funktioniert auch komplett ohne API-Key und ohne Internet mit über 50 handgeschriebenen witzigen deutschen Sprüchen!
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
- **💤 Schlaf- & DND-Nachtmodus (Deep Sleep)**:
  - Rechtsklick ➔ *💤 Schlafen legen (Zzz... DND)*: Yuyu rollt sich friedlich zusammen, blaue `Zzz...`-Partikel steigen auf.
  - Im Schlafmodus sind alle Nervensägen-Alarme stummgeschaltet, damit du ungestört arbeiten kannst.
- **🍅 Pomodoro Fokus-Trainer (25m / 5m)**:
  - Integrierter Pomodoro-Timer im HUD. Yuyu feuert dich an und ruft nach 25 Minuten pünktlich zur 5-Minuten-Pause auf.
- **⭐ RPG Progression & Level-System**:
  - Sammle Erfahrungspunkte (XP) für jedes getrunkene Glas Wasser (+25 XP), Pausen (+35 XP), Snacks, Streicheln (+15 XP) und Fangspiele!
  - Steige auf: *Neuling* ➔ *Bekannter* ➔ *Kumpel* ➔ *Guter Freund* ➔ *Bester Freund* ➔ *Seelenverwandter*!
- **🍽️ Snack-Bar (5 verschiedene Snacks)**:
  - 🥪 *Sandwich / Mahlzeit* (+50% Hunger)
  - 🍎 *Knackiger Apfel* (+25% Hunger, +10% Vitalität)
  - ☕ *Heißer Kaffee / Espresso* (+40% Energie-Boost)
  - 🥤 *Frisches Glas Wasser* (+50% Hydration)
  - 🍩 *Süßer Donut* (+30% Hunger, +10 Zuneigung)
- **🎵 Pure Python Retro-Soundeffekte (SFX)**:
  - Eingebauter Synthesizer mit 9 Chimes: *Happy, Level-Up, Alert, Ball-Catch, Sleep, Pomodoro, Purr, Dice, Fortune*.
  - Getrenntes Stummschalten von Effekten und Stimme im Menü und Einstellungsdialog.
- **🎨 4 Wählbare HUD-Themes**:
  - 🔵 **Cyberpunk Neon** (Cyan & Dunkelblau)
  - 🟢 **Gameboy Retro** (Vintage Matrix-Grün)
  - 🌸 **Kawaii Pastel** (Sakura-Rosa & Flieder)
  - 🌙 **Minimal Slate** (Dezentes Schiefergrau & Silber)
- **📊 Health-Dashboard & Statistiken**:
  - Zählt getrunkene Gläser Wasser, Mahlzeiten, Pausen, Pomodoros und konsekutive Streak-Tage!
- **📝 Desktop Haftnotiz (Quick-Memo)**:
  - Kleiner gelber Notizzettel direkt über Yuyu anheftbar für schnelle Aufgaben, Ideen oder Einkaufszettel.
- **🖥️ KDE Plasma System-Tray Integration**:
  - Unauffälliges Symbol in der Taskleiste mit Live-Status im Tooltip und Schnell-Aktionen.
- **🔍 Stufenloses Mausrad-Zoomen (Ctrl + Scrollen)**:
  - Halte die Strg-Taste gedrückt und scrolle mit dem Mausrad über Yuyu (35% bis 130%).
- **🎨 Kristallklares Rendering & Wayland-Kompatibilität**:
  - Bilineare Kantenglättung (`SmoothTransformation`) – gestochen scharf.
  - Erzwingt `QT_QPA_PLATFORM=xcb` (XWayland) für flüssiges Roaming und Drag & Drop unter CachyOS / KDE Plasma.
- **⚡ Volle Terminal CLI-Steuerung**:
  - `desktop-pet --status` (Status-Dashboard im Terminal)
  - `desktop-pet --pet` (Streicheln & Zuneigung)
  - `desktop-pet --dice` (Würfeln)
  - `desktop-pet --fortune` (Glückskeks)
  - `desktop-pet --skins` (Skins auflisten)
  - `desktop-pet --feed [snack]` / `--drink` / `--break` / `--say "Text"`

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
