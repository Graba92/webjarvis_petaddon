# 🐾 Desktop Pet & Tamagotchi AI Companion v2.6 (OpenPets Mini Core)

[🇩🇪 Switch to German Documentation](README_DE.md) | [🇬🇧 English Documentation](README.md)

An interactive, animated **100% standalone Linux Desktop Companion** and **Tamagotchi**, inspired by **OpenPets**. Runs directly on your Linux desktop (KDE Plasma / CachyOS / X11 / Wayland) as a frameless, transparent always-on-top window with OpenPets V2 gaze tracking, autonomous roaming, 4 selectable character voices, Tamagotchi vitals system, and a witty **nagging companion** reminding you to take breaks, drink water, eat, and attend appointments!

---

## ✨ Features & New Highlights (v2.6)

- **🖥️ 100% Standalone Desktop Companion**: Completely independent PyQt6 application running floating on your desktop – no web browser or external servers needed.
- **💖 Interactive Petting & Purring Engine**:
  - Double-click or select *💖 Streicheln & Kraulen*: Yuyu purrs with custom audio (`purr.wav`), displays happy hearts particles, and gains +15 XP & +10 Affection.
- **🎮 Minigames & Fun**:
  - 🎾 **Interactive Ball Game (Fetch)**: Throw a tennis ball across your desktop with realistic gravity; Yuyu chases, catches it, and celebrates.
  - 🎲 **Dice Roll (1-6)**: Roll the dice with sound effects and witty developer commentary.
  - 🥠 **Developer Fortune Cookie**: Open a fortune cookie with chime sound and humorous coding wisdom.
- **🎭 Multi-Skin Manager & Skin Switcher**:
  - Drop custom pet folders into `pets/` or `~/.local/share/webjarvis_petaddon/pets/`.
  - Switch skins instantly from the right-click menu without restarting.
  - Check skins via CLI: `desktop-pet --skins`.
- **🧘 Ergonomics & Posture Coach**:
  - Quick reminder for posture correction, shoulder relaxation, and the 20-20-20 eye strain rule.
- **💻 Hardware & CPU Load Watcher**:
  - Monitors high system load (compiles, renders) and prompts humorous alerts with sweat drops (`💦`) to cool down.
- **🤖 Universal LLM Support via API Key**:
  - Works with **Google Gemini**, **OpenAI**, **Groq**, **OpenRouter**, **Ollama**, or any custom Base URL.
  - Auto-detects key prefixes (`AIzaSy...`, `sk-...`, `gsk_...`).
  - **Offline Resilience:** Runs completely offline without API keys using 50+ handcrafted hilarious German lines.
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
- **💤 Deep Sleep & DND Night Mode**:
  - Right-click ➔ *💤 Put to sleep (Zzz...)*: Yuyu curls up peacefully with floating `Zzz...` particles. In sleep mode, all nagging alarms are muted for distraction-free focus or resting.
- **🍅 Integrated Pomodoro Focus Coach**:
  - Built-in Pomodoro timer in the HUD (25 min focus / 5 min break) with cheer-on phrases and break notifications.
- **⭐ RPG Progression & Level-Up System**:
  - Earn XP for drinking water (+25 XP), taking screen breaks (+35 XP), eating snacks, petting (+15 XP), and playing fetch!
  - Level up from *Rookie* to *Soulmate*!
- **🍽️ Snack-Bar (5 Interactive Snacks)**:
  - 🥪 *Sandwich / Meal* (+50% Hunger)
  - 🍎 *Crisp Apple* (+25% Hunger, +10% Vitality)
  - ☕ *Hot Coffee / Espresso* (+40% Energy Boost)
  - 🥤 *Fresh Glass of Water* (+50% Hydration)
  - 🍩 *Sweet Donut* (+30% Hunger, +10 Affection)
- **🎵 Pure Python Retro Sound Effects (SFX)**:
  - Built-in synthesizer without external dependencies: 9 chimes (*Happy, Level-Up, Alert, Ball-Catch, Sleep, Pomodoro, Purr, Dice, Fortune*).
  - Separate toggles to mute SFX and Voice in menus and settings.
- **🎨 4 Selectable HUD Themes**:
  - 🔵 **Cyberpunk Neon** (Cyan & Deep Blue)
  - 🟢 **Gameboy Retro** (Vintage Matrix Green)
  - 🌸 **Kawaii Pastel** (Sakura Pink & Lilac)
  - 🌙 **Minimal Slate** (Refined Slate Gray & Silver)
- **📊 Health Dashboard & Daily Tracker**:
  - Monitors glasses of water, meals, screen breaks, Pomodoro counts, and consecutive active streak days!
- **📝 Desktop Sticky Note (Quick-Memo)**:
  - Pin a small yellow sticky memo directly over Yuyu for quick reminders, ideas, or to-dos.
- **🖥️ KDE Plasma System-Tray Integration**:
  - Discreet tray icon in your system panel with live status tooltip and quick-actions (show/hide, feed, break).
- **🔍 Smooth Mouse-Wheel Zooming (Ctrl + Scroll)**:
  - Hold Ctrl and scroll over Yuyu to scale smoothly between 35% and 130%.
- **🎨 Anti-Aliased Bilinear Rendering & Wayland Support**:
  - Smooth bilinear texture sampling (`SmoothTransformation`) without pixelation.
  - Enforces `QT_QPA_PLATFORM=xcb` (XWayland) for unrestricted `move()`, roaming and drag & drop on KDE Plasma Wayland.
- **⚡ Full Terminal CLI Control**:
  - `desktop-pet --status` (Show status dashboard in CLI)
  - `desktop-pet --pet` (Pet the companion)
  - `desktop-pet --dice` (Roll dice)
  - `desktop-pet --fortune` (Read fortune cookie)
  - `desktop-pet --skins` (List available skins)
  - `desktop-pet --feed [snack]` / `--drink` / `--break` / `--say "Text"`

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
- **Configuration:** Right-click the pet ➔ *⚙️ Settings & Dashboard...*

---

## 📜 License

MIT License. Developed by Matthias Haase (Graba92) for the Valhalla Tools Suite.
