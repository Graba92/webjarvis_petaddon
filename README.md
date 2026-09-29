# 🐾 Desktop Pet & Tamagotchi AI Companion (OpenPets Mini Core)

[🇩🇪 Switch to German Documentation](README_DE.md) | [🇬🇧 English Documentation](README.md)

An interactive, animated **100% standalone Linux Desktop Companion** and **Tamagotchi**, inspired by **OpenPets**. Runs directly on your Linux desktop (KDE Plasma / CachyOS / X11 / Wayland) as a frameless, transparent always-on-top window with OpenPets V2 gaze tracking, autonomous roaming, 4 selectable character voices, Tamagotchi vitals system, and a witty **nagging companion** reminding you to take breaks, drink water, eat, and attend appointments!

---

## ✨ Highlights

- **🖥️ 100% Standalone Desktop Companion**: Completely independent PyQt6 application running floating on your desktop – no web browser or external servers needed.
- **🤖 Universal LLM Support via API Key**:
  - Works with **Google Gemini**, **OpenAI**, **Groq**, **OpenRouter**, **Ollama**, or any custom Base URL.
  - Auto-detects key prefixes (`AIzaSy...`, `sk-...`, `gsk_...`).
  - **Offline Resilience:** Runs completely offline without API keys using 40+ handcrafted hilarious German & English lines.
- **🎙️ 4 Distinct Character Voices**:
  1. 👧 **Lola**: Female, energetic, bubbly & cheeky (Pitch 1.28)
  2. 👦 **Buster**: Male, sarcastic, snappy & dynamic (Pitch 0.95)
  3. 🌸 **Mimi**: Female, gentle, sweet & caring (Pitch 1.10)
  4. 🧔 **Klaus**: Male, dry, deep & brutally honest (Pitch 0.78)
  - Quick-switchable via right-click menu or settings GUI with sample audio preview.
- **🐾 Real Tamagotchi Vitals & Live HUD**:
  - Displays 3 progress bars directly above the pet's head:
    - 🥪 **Hunger / Food** (0 - 100%, decreases over time)
    - 💧 **Thirst / Water** (0 - 100%, warns against dehydration)
    - ⚡ **Energy / Screen Break** (0 - 100%, prevents burnout and eye strain)
    - 📅 **Next Appointment & Countdown**
  - **Color-coded:** Green (>50%) ➔ Yellow (25-50%) ➔ Urgent Red (<25%).
- **😼 The Little Pest / Nagging Companion**:
  - When any vital drops below 25%, Yuyu refuses to let you stay idle:
    - Jumps up and down frantically.
    - Shows an animated comic speech bubble.
    - Vocally calls you out out loud using its character voice!
  - Adjustable nagging intensity: *Gentle Reminder*, *Cheeky Buddy* or *Extreme Pest*.
- **🥪 Interactive Care ("Feed & Drink")**:
  - Right-click the pet for immediate interactions:
    - 🥪 *Ate a snack / meal* (+50% hunger)
    - 💧 *Drank a glass of water* (+50% thirst)
    - 🧘 *Took a break & stretched* (+100% energy)
- **📅 Appointment & Reminder Manager**:
  - Schedule tasks and meetings with date and time.
  - The pet alerts you on time via voice and speech bubble.
- **🎨 Anti-Aliased Bilinear Rendering & Wayland Support**:
  - Smooth bilinear texture sampling (`SmoothTransformation`) without pixelation.
  - Enforces `QT_QPA_PLATFORM=xcb` (XWayland) for unrestricted `move()`, roaming and drag & drop on KDE Plasma Wayland.
- **👁️ 16-Sector Gaze Tracking**: Looks curiously towards your desktop mouse cursor.
- **🚶 Autonomous Roaming**: Strolls along the bottom of your screen.

---

## 🚀 Persistent OS Installation & Usage

Run the installation script to install the companion permanently into `~/.local/share/webjarvis_petaddon`:

```bash
chmod +x install.sh
./install.sh
```

After installation:
- **CLI Command:** `desktop-pet` (or `webjarvis-pet`)
- **Application Menu:** Listed under *Utilities / Amusement* as "Desktop Pet & Tamagotchi AI (Yuyu)"
- **Configuration:** Right-click the pet ➔ *⚙️ Settings & AI Configuration...*

---

## 📜 License

MIT License. Developed by Matthias Haase (Graba92) for the Valhalla Tools Suite.
