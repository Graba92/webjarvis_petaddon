# 🐾 WebJarvis Desktop Pet (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

An interactive, animated **native Linux Desktop Companion** for **WebJarvis** inspired by **OpenPets**. Running directly over your Linux desktop (KDE Plasma / CachyOS) as a frameless, transparent, hardware-accelerated overlay window with OpenPets V2 gaze tracking, autonomous roaming, and live WebSocket telemetry reactions.

![WebJarvis Pet Preview](pets/yuyu-chibi/spritesheet.webp)

---

## ✨ Features

- **🖥️ True Desktop Overlay**: Runs natively on your desktop using PyQt6 with transparent alpha pass-through (`Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`).
- **🎮 OpenPets V2 Compatibility**: Native rendering of 8×11 sprite atlases (192×208 frame dimension) matching OpenPets Codex V2 specifications.
- **👁️ 16-Sector Desktop Cursor Gaze**: Real-time eye and head tracking (Rows 9 & 10) following your mouse cursor across the entire screen.
- **🚶 Autonomous Desktop Roaming**: Wanders naturally along the bottom screen edge with smart boundary collision bounce and pauses.
- **🎙️ Right-Click Voice Selection**: Right-click directly on the pet on your desktop to switch Jarvis TTS voices:
  - 👨 **Male Voice (Puck / Standard)**
  - 👩 **Female Voice (Aoede / Soft & Natural)**
- **🔄 Live J.A.R.V.I.S. Telemetry (ws://127.0.0.1:8765)**:
  - `THINKING` ➜ Reviews & analyzes (Row 8).
  - `SPEAKING` ➜ Waves & displays floating speech bubbles with Jarvis voice responses right above the pet.
  - `LISTENING` / `CONFIRM` ➜ Waiting animation (Row 6).
  - `ERROR` ➜ Expresses concern (Row 5).
  - `IDLE` ➜ Relaxed blinking and neutral pose (Row 0).
- **🖱️ Drag & Drop**: Click and drag Yuyu anywhere across your monitors.
- **⚡ 1-Click Launch from WebJarvis**: Click the **🐾 Cat Icon** in the WebJarvis Bottom Dock or Hardware Control Center to spawn or dismiss the pet.

---

## 🚀 Quick Start & Launch

Run the desktop pet directly:
```bash
./run.sh
```

Or trigger it from within the WebJarvis web interface / control center!

---

## 📄 License

MIT License. Designed & engineered by Matthias Haase (Graba92) for the Valhalla Suite.
