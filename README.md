# 🐾 WebJarvis Desktop Pet (OpenPets Mini Core)

[🇩🇪 Zur deutschen Dokumentation wechseln](README_DE.md) | [🇬🇧 Switch to English Documentation](README.md)

An interactive, animated **native Linux Desktop Companion** for **WebJarvis** inspired by **OpenPets**. Running directly over your Linux desktop (KDE Plasma / CachyOS) as a frameless, transparent, hardware-accelerated overlay window with OpenPets V2 gaze tracking, autonomous roaming, live voice switching, and bidirectional WebSocket telemetry reactions.

![WebJarvis Pet Preview](pets/yuyu-chibi/spritesheet.webp)

---

## ✨ Features

- **🖥️ True Desktop Overlay**: Runs natively on your desktop using PyQt6 with transparent alpha pass-through (`Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`).
- **🎨 Studio-Quality Anti-Aliasing**: Completely eliminates pixelation using bilinear smooth transform filtering (`Qt.TransformationMode.SmoothTransformation`).
- **🎮 OpenPets V2 Compatibility**: Native rendering of 8×11 sprite atlases (192×208 frame dimension) matching OpenPets Codex V2 specifications.
- **👁️ 16-Sector Desktop Cursor Gaze**: Real-time eye and head tracking (Rows 9 & 10) following your actual mouse cursor across the entire screen.
- **🚶 Autonomous Desktop Roaming**: Wanders naturally along the bottom screen edge with smart boundary collision bounce and pauses.
- **🎙️ Right-Click Live Voice Switching (No Restart Needed)**:
  - 👨 **Male Voice (Puck / Standard)**
  - 👩 **Female Voice (Aoede / Soft & Natural)**
  - Reconnects the Gemini Live session dynamically in real time!
- **⚡ Desktop Jarvis Controls**:
  - 🎤 Toggle Microphone (Mute / Unmute)
  - ⏹️ Stop speech output (Interrupt)
  - 🌐 1-Click open WebJarvis Webinterface (`http://localhost:3000`)
- **🖱️ Interactive Drag & Drop**: Grab Yuyu and move her anywhere on your desktop — WebJarvis notices the movement and responds vocally!
- **🔄 Live J.A.R.V.I.S. Telemetry (ws://127.0.0.1:8765)**:
  - `THINKING` ➜ Reviews & analyzes (Row 8).
  - `SPEAKING` ➜ Waves & displays floating speech bubbles with Jarvis voice responses right above the pet.
  - `audio_level` ➜ Bounces gently in rhythm with Jarvis speech!
  - `LISTENING` / `CONFIRM` ➜ Waiting animation (Row 6).
  - `ERROR` ➜ Expresses concern (Row 5).
  - `IDLE` ➜ Relaxed blinking and neutral pose (Row 0).

---

## 🚀 Persistent OS Installation & Launch

Run the installer to set up the tool permanently in `~/.local/share/webjarvis_petaddon`:

```bash
chmod +x install.sh
./install.sh
```

After installation:
- **CLI Command:** `webjarvis-pet`
- **Application Menu:** Listed under Utilities / Dienstprogramme in KDE Plasma
- **From WebJarvis:** Click the **🐾 Cat Icon** in the Bottom Dock or Hardware Control Center to start or dismiss Yuyu!

---

## 📄 License

MIT License. Designed & engineered by Matthias Haase (Graba92) for the Valhalla Suite.
