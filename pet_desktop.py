#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐾 Desktop Pet & Tamagotchi AI Companion v2.5 (OpenPets Mini Core)
Eigenständiges, plattformübergreifendes Linux Desktop-Overlay (KDE Plasma / CachyOS / X11 / Wayland).

Erweiterte Features:
- 100% Standalone (Keine Abhängigkeit von WebJarvis oder externen Servern)
- Universelle LLM-Konfiguration: Kompatibel mit jedem LLM (Gemini, OpenAI, OpenRouter, Groq, Ollama) über API-Key
- 4 Charakter-Stimmen (Lola, Buster, Mimi, Klaus) mit Neural-TTS / Fallback
- Echtes Tamagotchi-System: Hunger, Durst, Energie/Pause & Termine mit Live-Statusanzeige über dem Pet
- Die kleine Nervensäge: Erinnert aktiv, frech und humorvoll an Trinken, Pausen, Essen und Termine
- 🎾 Interaktives Ball-Fangspiel (Fetch Game) mit Desktop-Physik & Ball-Jagd
- 💤 Schlaf- & DND-Nachtmodus (Deep Sleep) mit Zzz-Partikeln & stummen Alarmen
- 🍅 Integrierter Pomodoro-Fokus-Trainer (25 Min Arbeit / 5 Min Pause) mit Pet-Anfeuerung
- ⭐ RPG Progression & Level-System (XP für Wasser, Pausen, Snacks, Zuneigung)
- 🍔 Snack-Bar (Sandwich, Apfel, Kaffee, Wasser, Donut) mit schwebenden Emojis & SFX
- 🎵 Akustische Retro-Soundeffekte (Chimes für Füttern, Level-Up, Notstand, Pomodoro)
- 🎨 4 wählbare HUD-Themes (Cyberpunk Neon, Gameboy Retro, Kawaii Pastel, Minimal Slate)
- 📊 Ausführliches Health-Dashboard & Statistiken (Tageszähler & Streak)
- Kristallklares Rendering mit bilinearem Anti-Aliasing (SmoothTransformation)
- Wayland / KDE Plasma kompatibel durch erzwungenes XWayland (xcb)
- 16-Sektoren Blickverfolgung & autonomes Roaming entlang des Bildschirms
"""

import os
import sys

# Linux Wayland / KDE Plasma Fix:
if "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

import math
import time
import json
import random
import wave
import struct
import urllib.request
import urllib.parse
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPointF, QRect, QRectF, pyqtSignal, QObject, QDate, QTime
)
from PyQt6.QtGui import (
    QPainter, QImage, QPixmap, QColor, QFont, QCursor, QAction, QActionGroup,
    QPen, QBrush, QLinearGradient, QIcon
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSlider, QCheckBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTimeEdit, QDateEdit, QSpinBox, QGroupBox, QProgressBar,
    QSystemTrayIcon, QInputDialog
)

# OpenPets Codex V2 Spritesheet Spezifikation
FRAME_WIDTH = 192
FRAME_HEIGHT = 208
SPRITE_COLS = 8
SPRITE_ROWS = 11

ANIMATIONS = {
    "idle": {"row": 0, "frames": 6, "duration_ms": 4000, "loop": True},
    "running-right": {"row": 1, "frames": 8, "duration_ms": 950, "loop": True},
    "running-left": {"row": 2, "frames": 8, "duration_ms": 950, "loop": True},
    "waving": {"row": 3, "frames": 4, "duration_ms": 700, "loop": False},
    "jumping": {"row": 4, "frames": 5, "duration_ms": 840, "loop": False},
    "failed": {"row": 5, "frames": 8, "duration_ms": 1220, "loop": False},
    "waiting": {"row": 6, "frames": 6, "duration_ms": 1010, "loop": True},
    "running": {"row": 7, "frames": 6, "duration_ms": 800, "loop": True},
    "review": {"row": 8, "frames": 6, "duration_ms": 1030, "loop": True},
}

# 4 Auswählbare Stimmen
VOICES = {
    "lola": {
        "name": "Lola (Weiblich - Frech & Lebhaft)",
        "pitch": 1.28,
        "rate": 1.05,
        "espeak": "de+f2",
        "description": "Quirlig, verspielt und neckisch"
    },
    "buster": {
        "name": "Buster (Männlich - Sarkastisch & Dynamisch)",
        "pitch": 0.95,
        "rate": 1.15,
        "espeak": "de+m3",
        "description": "Schlagfertig, direkt und frech"
    },
    "mimi": {
        "name": "Mimi (Weiblich - Sanft & Fürsorglich)",
        "pitch": 1.10,
        "rate": 0.95,
        "espeak": "de+f4",
        "description": "Besorgt, liebevoll mahnend"
    },
    "klaus": {
        "name": "Klaus (Männlich - Tief & Trocken)",
        "pitch": 0.78,
        "rate": 0.92,
        "espeak": "de+m1",
        "description": "Brummig, trocken und schonungslos ehrlich"
    }
}

# 4 Wählbare HUD Themes
HUD_THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "bg": QColor(10, 15, 25, 220),
        "border": QColor(0, 212, 255, 140),
        "text": QColor(255, 255, 255),
        "accent": QColor(0, 212, 255),
        "hunger": QColor(34, 197, 94),
        "thirst": QColor(6, 182, 212),
        "energy": QColor(245, 158, 11)
    },
    "gameboy": {
        "name": "Gameboy Retro",
        "bg": QColor(15, 56, 15, 230),
        "border": QColor(139, 172, 15, 180),
        "text": QColor(155, 188, 15),
        "accent": QColor(139, 172, 15),
        "hunger": QColor(139, 172, 15),
        "thirst": QColor(48, 98, 48),
        "energy": QColor(139, 172, 15)
    },
    "kawaii": {
        "name": "Kawaii Pastel",
        "bg": QColor(30, 20, 35, 220),
        "border": QColor(244, 114, 182, 160),
        "text": QColor(255, 240, 245),
        "accent": QColor(244, 114, 182),
        "hunger": QColor(251, 146, 60),
        "thirst": QColor(167, 139, 250),
        "energy": QColor(244, 114, 182)
    },
    "minimal": {
        "name": "Minimal Slate",
        "bg": QColor(24, 28, 38, 225),
        "border": QColor(100, 116, 139, 140),
        "text": QColor(226, 232, 240),
        "accent": QColor(148, 163, 184),
        "hunger": QColor(52, 211, 153),
        "thirst": QColor(56, 189, 248),
        "energy": QColor(251, 191, 36)
    }
}

# Level-Titel
LEVEL_TITLES = [
    (0, "Neuling"),
    (100, "Bekannter"),
    (250, "Kumpel"),
    (500, "Guter Freund"),
    (900, "Bester Freund"),
    (1500, "Seelenverwandter"),
    (2500, "Unzertrennlich ✨")
]

# Offline-Repertoire für freche Nervensägen-Sprüche
OFFLINE_NAG_LINES = {
    "thirst": [
        "Hallo?! Vertrocknest du gerade vor dem Monitor? Trink gefälligst ein Glas Wasser!",
        "Alarm im Hydrations-Speicher! Du bist doch kein Wüstenkaktus. Trink was!",
        "Wasser-Level kritisch! Steh auf und hol dir ein Glas, sonst nerve ich weiter!",
        "Dein Gehirn besteht zu 75% aus Wasser – und aktuell bist du trocken wie Knäckebrot! Wasser marsch!",
        "Trinkpause JETZT! Kein Pardon mehr!"
    ],
    "energy": [
        "Augen weg vom Bildschirm! Du starrst schon viel zu lange auf den Code! Steh auf, dehn dich!",
        "Ergonomie-Alarm! Deine Wirbelsäule weint schon leise. Mach 5 Minuten Pause!",
        "Sitzfleisch überhitzt! Roll die Schultern, atme tief durch und streck dich!",
        "Pause machen ist keine Schwäche, sondern Wartung! 5 Minuten Auszeit, los jetzt!",
        "Ich streike gleich, wenn du nicht sofort kurz vom Schreibtisch aufstehst!"
    ],
    "hunger": [
        "Maaaagen knuuuuurrt! Dein Körper braucht Treibstoff! Mach dir was zu essen!",
        "Hey Workaholic! Zeit für 'nen Snack oder 'ne richtige Mahlzeit! Geh in die Küche!",
        "Konzentration sinkt, Blutzucker im Keller! Iss gefälligst was Anständiges!",
        "Ich rieche Essen... ach nee, das ist nur meine Sehnsucht. Fütter deinen Körper!",
        "Essen fassen! Der Schreibtisch läuft dir nicht weg!"
    ],
    "appointment": [
        "Achtung, Schlafmütze! Dein Termin '{title}' steht um {time} Uhr an!",
        "Termin-Alarm! In wenigen Minuten geht's los: '{title}'! Nicht verpennen!",
        "Erinnerung vom Dienst: '{title}' um {time} Uhr! Bereit machen!",
        "Du hast einen wichtigen Termin: '{title}' ({time} Uhr)! Ich hab dich gewarnt!"
    ],
    "click": [
        "Hey! Nicht so kitzeln! 🐾",
        "Ich hab dich im Blick! 👁️",
        "Was gibt's, Chef? Pause fällig?",
        "Yuyu ist stets wachsam! ✨",
        "Klick mich nicht so wild an, bring mir lieber Wasser!"
    ],
    "drag": [
        "Huiii! Neuer Aussichtspunkt auf deinem Desktop! 🚀",
        "Rundflug beendet! Von hier aus sehe ich alles!",
        "Sanfte Landung! Schön hier oben!",
        "Positionswechsel erfolgreich! Ich behalte dich im Auge!",
        "Wo fliegen wir denn hin? CachyOS von oben sieht gut aus!"
    ]
}


# ==============================================================================
# 1. AKUSTISCHER RETRO SOUND-SYNTHESIZER (PURE PYTHON SFX)
# ==============================================================================
class RetroSoundSynthesizer:
    """Erzeugt 16-Bit PCM Chimes für Spiele, Notstände & Level-Ups ohne externe Libs"""

    CACHE_DIR = Path("/tmp/desktop_pet_sfx")

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_chimes()

    def _generate_wav(self, path: Path, freqs: List[float], tone_dur: float, decay: float, vol: float = 0.5):
        sample_rate = 22050
        frames = []
        for f in freqs:
            n_samples = int(sample_rate * tone_dur)
            for s in range(n_samples):
                t = s / sample_rate
                env = math.exp(-decay * (s / n_samples))
                val = math.sin(2.0 * math.pi * f * t) * vol * env
                sample = int(val * 32767.0)
                frames.append(struct.pack('<h', max(-32768, min(32767, sample))))

        with wave.open(str(path), 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))

    def _ensure_chimes(self):
        # 1. Happy Chime (Arpeggio C5 -> E5 -> G5 -> C6)
        p_happy = self.CACHE_DIR / "happy.wav"
        if not p_happy.exists():
            self._generate_wav(p_happy, [523.25, 659.25, 783.99, 1046.50], 0.08, 3.0, 0.45)

        # 2. Level-Up Fanfare (C5 -> E5 -> G5 -> B5 -> C6 -> E6)
        p_lvl = self.CACHE_DIR / "level_up.wav"
        if not p_lvl.exists():
            self._generate_wav(p_lvl, [523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51], 0.09, 2.0, 0.55)

        # 3. Alert / Notstand Chime (A5 -> E6)
        p_alert = self.CACHE_DIR / "alert.wav"
        if not p_alert.exists():
            self._generate_wav(p_alert, [880.0, 1318.51, 880.0, 1318.51], 0.10, 2.5, 0.45)

        # 4. Ball Catch / Pop Chime (F4 -> C5 -> G5)
        p_ball = self.CACHE_DIR / "ball_catch.wav"
        if not p_ball.exists():
            self._generate_wav(p_ball, [349.23, 523.25, 783.99], 0.07, 4.0, 0.5)

        # 5. Sleep / Lullaby Chime (G5 -> E5 -> C5)
        p_sleep = self.CACHE_DIR / "sleep.wav"
        if not p_sleep.exists():
            self._generate_wav(p_sleep, [783.99, 659.25, 523.25], 0.16, 1.8, 0.35)

        # 6. Pomodoro Gong (G4 -> C5)
        p_pomo = self.CACHE_DIR / "pomodoro.wav"
        if not p_pomo.exists():
            self._generate_wav(p_pomo, [392.0, 523.25], 0.30, 1.5, 0.5)

    def play(self, sfx_name: str, volume: float = 0.8):
        wav_path = self.CACHE_DIR / f"{sfx_name}.wav"
        if wav_path.exists():
            threading.Thread(
                target=lambda: subprocess.run(["pw-play", "--volume", str(volume), str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
                daemon=True
            ).start()


# ==============================================================================
# 2. SCHWEBENDE PARTIKEL-ENGINE (HEARTS, STARS, ICONS, ZZZ)
# ==============================================================================
class Particle:
    def __init__(self, x: float, y: float, text: str, color: QColor, vx: float = 0.0, vy: float = -1.2, max_life: float = 2.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.vx = vx
        self.vy = vy
        self.birth = time.time()
        self.max_life = max_life

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        return (time.time() - self.birth) < self.max_life

    def alpha(self) -> float:
        age = time.time() - self.birth
        return max(0.0, 1.0 - (age / self.max_life))


# ==============================================================================
# 3. INTERAKTIVES BALL-FANGSPIEL (FETCH GAME)
# ==============================================================================
class BallGame:
    def __init__(self):
        self.active = False
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.target_caught = False

    def throw(self, start_x: float, start_y: float, target_x: float):
        self.active = True
        self.target_caught = False
        self.x = start_x
        self.y = start_y
        self.vx = (target_x - start_x) * 0.04
        self.vy = -7.5  # Bogenwurf

    def update_physics(self, ground_y: float):
        if not self.active:
            return

        self.vy += 0.45  # Gravitation
        self.x += self.vx
        self.y += self.vy

        if self.y >= ground_y:
            self.y = ground_y
            self.vy = -self.vy * 0.65  # Abprallen
            self.vx *= 0.85  # Reibung
            if abs(self.vy) < 1.0:
                self.vy = 0.0


# ==============================================================================
# 4. POMODORO FOKUS-TRAINER
# ==============================================================================
class PomodoroManager(QObject):
    tick = pyqtSignal(str, int)  # mode, seconds_left
    finished = pyqtSignal(str)   # mode

    def __init__(self):
        super().__init__()
        self.mode = "OFF"  # OFF, FOCUS, BREAK
        self.seconds_left = 0
        self.total_focus_minutes = 25
        self.total_break_minutes = 5

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

    def start_focus(self, minutes: int = 25):
        self.mode = "FOCUS"
        self.total_focus_minutes = minutes
        self.seconds_left = minutes * 60
        self.timer.start(1000)

    def start_break(self, minutes: int = 5):
        self.mode = "BREAK"
        self.total_break_minutes = minutes
        self.seconds_left = minutes * 60
        self.timer.start(1000)

    def stop(self):
        self.mode = "OFF"
        self.timer.stop()

    def _on_tick(self):
        if self.mode == "OFF":
            return

        self.seconds_left -= 1
        self.tick.emit(self.mode, self.seconds_left)

        if self.seconds_left <= 0:
            completed_mode = self.mode
            if completed_mode == "FOCUS":
                self.start_break(self.total_break_minutes)
            else:
                self.stop()
            self.finished.emit(completed_mode)


# ==============================================================================
# 5. KONFIGURATIONS-MANAGER
# ==============================================================================
class ConfigManager:
    """Verwaltet dauerhafte Einstellungen in ~/.config/desktop_pet/config.json"""

    CONFIG_DIR = Path.home() / ".config" / "desktop_pet"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULT_CONFIG = {
        "api_key": "",
        "llm_provider": "auto",
        "model_name": "gemini-1.5-flash",
        "base_url": "",
        "voice": "lola",
        "volume": 85,
        "muted": False,
        "scale": 0.70,
        "hud_theme": "cyberpunk",
        "roaming_enabled": True,
        "show_tamagotchi_hud": True,
        "nag_intensity": "frech",
        "decay_minutes": {
            "hunger": 120,
            "thirst": 45,
            "energy": 50
        },
        "vitals": {
            "hunger": 85.0,
            "thirst": 90.0,
            "energy": 95.0,
            "last_tick": time.time()
        },
        "progression": {
            "xp": 35,
            "level": 1,
            "affection": 50,
            "water_drank_today": 2,
            "meals_eaten_today": 1,
            "breaks_taken_today": 1,
            "pomodoros_done_today": 0,
            "streak_days": 1,
            "last_active_date": datetime.now().strftime("%Y-%m-%d")
        },
        "appointments": [],
        "sticky_note": "",
        "pos_x": -1,
        "pos_y": -1
    }

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.data = dict(self.DEFAULT_CONFIG)
        self.load()
        self._check_midnight_reset()

    def load(self):
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Config] Fehler beim Laden: {e}")

    def save(self):
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Fehler beim Speichern: {e}")

    def _check_midnight_reset(self):
        prog = self.data.setdefault("progression", dict(self.DEFAULT_CONFIG["progression"]))
        last_date = prog.get("last_active_date", "")
        today = datetime.now().strftime("%Y-%m-%d")

        if last_date != today:
            # Tageszähler zurücksetzen, Streak erhöhen
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_date == yesterday:
                prog["streak_days"] = prog.get("streak_days", 1) + 1
            else:
                prog["streak_days"] = 1

            prog["water_drank_today"] = 0
            prog["meals_eaten_today"] = 0
            prog["breaks_taken_today"] = 0
            prog["pomodoros_done_today"] = 0
            prog["last_active_date"] = today
            self.save()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_xp(self, amount: int) -> bool:
        prog = self.data.setdefault("progression", dict(self.DEFAULT_CONFIG["progression"]))
        prog["xp"] = prog.get("xp", 0) + amount

        old_lvl = prog.get("level", 1)
        new_lvl = 1
        for threshold, title in LEVEL_TITLES:
            if prog["xp"] >= threshold:
                new_lvl += 1
            else:
                break
        new_lvl = max(1, new_lvl - 1)

        level_up = (new_lvl > old_lvl)
        prog["level"] = new_lvl
        self.save()
        return level_up

    def get_level_info(self) -> tuple:
        prog = self.data.get("progression", {})
        xp = prog.get("xp", 0)
        lvl = prog.get("level", 1)
        title = "Neuling"
        for t, tit in LEVEL_TITLES:
            if xp >= t:
                title = tit
        return lvl, title, xp


# ==============================================================================
# 6. AUDIO & SPRACHAUSGABE (VOICE ENGINE)
# ==============================================================================
class VoiceEngine(QObject):
    """Handhabt Sprachausgabe für 4 Stimmen mit Neural-TTS / Fallback und Audio-Rhythmus"""

    speech_started = pyqtSignal(str)
    speech_finished = pyqtSignal()
    audio_level = pyqtSignal(float)

    def __init__(self, config: ConfigManager, sfx: RetroSoundSynthesizer):
        super().__init__()
        self.config = config
        self.sfx = sfx
        self._is_speaking = False
        self._stop_requested = False

    def is_speaking(self) -> bool:
        return self._is_speaking

    def stop(self):
        self._stop_requested = True
        try:
            subprocess.run(["pkill", "-f", "pw-play.*pet_tts"], stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def speak(self, text: str, voice_override: Optional[str] = None):
        if self.config.get("muted", False) or not text.strip():
            return

        threading.Thread(
            target=self._speak_thread,
            args=(text, voice_override),
            daemon=True
        ).start()

    def _speak_thread(self, text: str, voice_override: Optional[str] = None):
        self._is_speaking = True
        self._stop_requested = False
        self.speech_started.emit(text)

        voice_key = voice_override or self.config.get("voice", "lola")
        voice_info = VOICES.get(voice_key, VOICES["lola"])

        tmp_raw = Path(f"/tmp/pet_tts_raw_{os.getpid()}.mp3")
        tmp_mod = Path(f"/tmp/pet_tts_mod_{os.getpid()}.mp3")

        played_successfully = False

        # 1. Methode: Google TTS + FFmpeg Pitch Shifting für 4 distinkte Stimmen
        try:
            url = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=de&q=" + urllib.parse.quote(text[:300])
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                audio_bytes = resp.read()

            with open(tmp_raw, "wb") as f:
                f.write(audio_bytes)

            pitch = voice_info.get("pitch", 1.0)
            rate = voice_info.get("rate", 1.0)

            sample_rate = int(24000 * pitch)
            tempo_correct = 1.0 / pitch * rate
            filter_str = f"asetrate={sample_rate},atempo={tempo_correct:.3f}"

            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", str(tmp_raw),
                "-af", filter_str,
                str(tmp_mod)
            ]
            res = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            play_file = tmp_mod if res.returncode == 0 and tmp_mod.exists() else tmp_raw

            vol = self.config.get("volume", 85) / 100.0
            play_proc = subprocess.Popen(["pw-play", "--volume", str(vol), str(play_file)])

            while play_proc.poll() is None and not self._stop_requested:
                lvl = random.uniform(0.25, 0.95)
                self.audio_level.emit(lvl)
                time.sleep(0.08)

            played_successfully = True
        except Exception:
            pass

        # 2. Methode: Offline espeak-ng Fallback
        if not played_successfully and not self._stop_requested:
            try:
                esp_voice = voice_info.get("espeak", "de+f2")
                esp_proc = subprocess.Popen(["espeak-ng", "-v", esp_voice, "-s", "155", text])
                while esp_proc.poll() is None and not self._stop_requested:
                    self.audio_level.emit(random.uniform(0.3, 0.8))
                    time.sleep(0.1)
            except Exception:
                try:
                    subprocess.run(["espeak", "-v", "de", text])
                except Exception:
                    pass

        self.audio_level.emit(0.0)
        self._is_speaking = False
        self.speech_finished.emit()

        for p in (tmp_raw, tmp_mod):
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass


# ==============================================================================
# 7. LLM ENGINE (EGAL WELCHES LLM ÜBER API-KEY)
# ==============================================================================
class LLMEngine:
    """Universelle Schnittstelle für Gemini, OpenAI, Groq, OpenRouter & Ollama"""

    def __init__(self, config: ConfigManager):
        self.config = config

    def detect_provider(self, key: str) -> str:
        k = key.strip()
        if k.startswith("AIzaSy"):
            return "gemini"
        elif k.startswith("sk-or-"):
            return "openrouter"
        elif k.startswith("gsk_"):
            return "groq"
        elif k.startswith("sk-"):
            return "openai"
        return "custom"

    def generate_nag(self, vital_type: str, context_info: str = "") -> str:
        api_key = self.config.get("api_key", "").strip()
        provider = self.config.get("llm_provider", "auto")

        if provider == "auto" and api_key:
            provider = self.detect_provider(api_key)

        intensity = self.config.get("nag_intensity", "frech")
        mood_instructions = {
            "sanft": "Sei fürsorglich, nett und sanft mahnend.",
            "frech": "Sei schlagfertig, humorvoll, frech und neckisch wie eine liebevolle Nervensäge.",
            "extrem": "Sei maximal nervig, dramatisch, ungeduldig und witzig übertrieben."
        }.get(intensity, "Sei frech und humorvoll.")

        system_prompt = (
            f"Du bist Yuyu Chibi, ein kleiner frecher Desktop-Tamagotchi-Begleiter auf einem Linux/CachyOS System. "
            f"{mood_instructions} "
            f"Erinnere den Nutzer an seine Gesundheit oder Termine. Antworte in genau 1-2 kurzen, knackigen deutschen Sätzen. "
            f"Keine langen Erklärungen, kein Smalltalk!"
        )

        user_prompt = f"Der Nutzer hat folgenden Notstand: {vital_type}. Info: {context_info}. Bring ihn jetzt dazu, sofort zu handeln!"

        if api_key:
            try:
                if provider == "gemini":
                    return self._call_gemini(api_key, system_prompt, user_prompt)
                elif provider in ("openai", "openrouter", "groq", "ollama", "custom"):
                    return self._call_openai_compat(api_key, provider, system_prompt, user_prompt)
            except Exception as e:
                print(f"[LLM] Fehler bei API-Aufruf ({provider}): {e}")

        # Offline Fallback
        lines = OFFLINE_NAG_LINES.get(vital_type, OFFLINE_NAG_LINES["thirst"])
        chosen = random.choice(lines)
        if vital_type == "appointment":
            chosen = chosen.replace("{title}", context_info).replace("{time}", datetime.now().strftime("%H:%M"))
        return chosen

    def _call_gemini(self, api_key: str, sys_prompt: str, user_prompt: str) -> str:
        model = self.config.get("model_name", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"System-Anweisung: {sys_prompt}\n\nAufgabe: {user_prompt}"}]}
            ],
            "generationConfig": {"maxOutputTokens": 80, "temperature": 0.8}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            candidates = res.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text.strip():
                    return text.strip()
        raise ValueError("Leere Gemini Antwort")

    def _call_openai_compat(self, api_key: str, provider: str, sys_prompt: str, user_prompt: str) -> str:
        base_urls = {
            "openai": "https://api.openai.com/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "groq": "https://api.groq.com/openai/v1",
            "ollama": "http://localhost:11434/v1"
        }
        base_url = self.config.get("base_url", "").strip() or base_urls.get(provider, "https://api.openai.com/v1")
        endpoint = base_url.rstrip("/") + "/chat/completions"

        model = self.config.get("model_name", "")
        if not model:
            if provider == "groq":
                model = "llama-3.3-70b-versatile"
            elif provider == "openrouter":
                model = "google/gemini-2.0-flash-exp:free"
            else:
                model = "gpt-4o-mini"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 80,
            "temperature": 0.8
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        with urllib.request.urlopen(req, timeout=6) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            choices = res.get("choices", [])
            if choices:
                msg = choices[0].get("message", {}).get("content", "")
                if msg.strip():
                    return msg.strip()
        raise ValueError("Leere Antwort")


# ==============================================================================
# 8. TAMAGOTCHI ENGINE (BEDÜRFNISSE, NERVENSÄGE, SNACKS & PROGRESSION)
# ==============================================================================
class TamagotchiEngine(QObject):
    """Simuliert Bedürfnisse, Termine, XP und Schlafrhythmus"""

    vitals_updated = pyqtSignal(dict)
    nag_triggered = pyqtSignal(str, str)
    level_up = pyqtSignal(int, str)

    def __init__(self, config: ConfigManager, llm: LLMEngine, voice: VoiceEngine, sfx: RetroSoundSynthesizer):
        super().__init__()
        self.config = config
        self.llm = llm
        self.voice = voice
        self.sfx = sfx

        vitals = self.config.get("vitals", {})
        self.hunger = float(vitals.get("hunger", 85.0))
        self.thirst = float(vitals.get("thirst", 90.0))
        self.energy = float(vitals.get("energy", 95.0))
        self.last_tick = vitals.get("last_tick", time.time())

        self.is_sleeping = False
        self.last_nag_time = 0.0
        self.nag_cooldown = 180.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _tick(self):
        now = time.time()
        elapsed = now - self.last_tick
        self.last_tick = now

        decay = self.config.get("decay_minutes", {"hunger": 120, "thirst": 45, "energy": 50})
        h_min = max(5, decay.get("hunger", 120))
        t_min = max(5, decay.get("thirst", 45))
        e_min = max(5, decay.get("energy", 50))

        if not self.is_sleeping:
            self.hunger = max(0.0, self.hunger - (100.0 / (h_min * 60.0)) * elapsed)
            self.thirst = max(0.0, self.thirst - (100.0 / (t_min * 60.0)) * elapsed)
            self.energy = max(0.0, self.energy - (100.0 / (e_min * 60.0)) * elapsed)
        else:
            # Im Schlaf regeneriert sich die Energie langsam!
            self.energy = min(100.0, self.energy + (100.0 / 1800.0) * elapsed)

        self.config.data["vitals"] = {
            "hunger": round(self.hunger, 1),
            "thirst": round(self.thirst, 1),
            "energy": round(self.energy, 1),
            "last_tick": now
        }

        self.vitals_updated.emit({
            "hunger": self.hunger,
            "thirst": self.thirst,
            "energy": self.energy
        })

        if not self.is_sleeping:
            self._check_appointments()

            if now - self.last_nag_time > self.nag_cooldown:
                critical = None
                if self.thirst < 25.0:
                    critical = "thirst"
                elif self.energy < 25.0:
                    critical = "energy"
                elif self.hunger < 25.0:
                    critical = "hunger"

                if critical:
                    self.last_nag_time = now
                    self.sfx.play("alert")
                    threading.Thread(target=self._trigger_nag_async, args=(critical,), daemon=True).start()

    def _trigger_nag_async(self, vital_type: str):
        val = int(getattr(self, vital_type, 0))
        nag_text = self.llm.generate_nag(vital_type, f"Aktueller Wert: {val}%")
        self.nag_triggered.emit(vital_type, nag_text)
        self.voice.speak(nag_text)

    def _check_appointments(self):
        appointments = self.config.get("appointments", [])
        now_str = datetime.now().strftime("%H:%M")
        today_str = datetime.now().strftime("%Y-%m-%d")

        for app in appointments:
            if app.get("date") == today_str and not app.get("reminded", False):
                if app.get("time", "") == now_str:
                    app["reminded"] = True
                    self.config.save()
                    title = app.get("title", "Termin")
                    msg = self.llm.generate_nag("appointment", title)
                    self.sfx.play("alert")
                    self.nag_triggered.emit("appointment", msg)
                    self.voice.speak(msg)
                    break

    def feed_snack(self, snack_type: str) -> tuple:
        """Gibt Snack, erneuert Vitals, gibt XP und spielt Sound"""
        prog = self.config.data.setdefault("progression", {})

        if snack_type == "sandwich":
            self.hunger = min(100.0, self.hunger + 50.0)
            prog["meals_eaten_today"] = prog.get("meals_eaten_today", 0) + 1
            msg = "Mmh, Sandwich verputzt! Großartig!"
            icon = "🥪"
            xp = 20
        elif snack_type == "apple":
            self.hunger = min(100.0, self.hunger + 25.0)
            self.energy = min(100.0, self.energy + 10.0)
            msg = "Knackiger Apfel! Vitamine für uns beide!"
            icon = "🍎"
            xp = 15
        elif snack_type == "coffee":
            self.energy = min(100.0, self.energy + 40.0)
            msg = "Kaffee-Boost aktiviert! Koffein im System!"
            icon = "☕"
            xp = 15
        elif snack_type == "water":
            self.thirst = min(100.0, self.thirst + 50.0)
            prog["water_drank_today"] = prog.get("water_drank_today", 0) + 1
            msg = "Aah, frisches Wasser! Hydration perfekt!"
            icon = "🥤"
            xp = 25
        elif snack_type == "donut":
            self.hunger = min(100.0, self.hunger + 30.0)
            prog["affection"] = min(100, prog.get("affection", 50) + 10)
            msg = "Ein Donut! Du bist ja so lieb zu mir! 💖"
            icon = "🍩"
            xp = 20
        else:
            return "Danke!", "✨"

        self.sfx.play("happy")
        is_lvl_up = self.config.add_xp(xp)
        self.config.save()

        if is_lvl_up:
            lvl, tit, _ = self.config.get_level_info()
            self.sfx.play("level_up")
            self.level_up.emit(lvl, tit)
            self.voice.speak(f"Juhu! Wir haben Level {lvl} erreicht! Wir sind jetzt {tit}!")

        return msg, icon

    def take_break(self):
        self.energy = 100.0
        prog = self.config.data.setdefault("progression", {})
        prog["breaks_taken_today"] = prog.get("breaks_taken_today", 0) + 1
        is_lvl = self.config.add_xp(35)
        self.sfx.play("happy")
        self.config.save()
        if is_lvl:
            lvl, tit, _ = self.config.get_level_info()
            self.level_up.emit(lvl, tit)
        self.voice.speak("Super durchgeatmet und gestreckt! Das tat gut! ✨")

    def toggle_sleep(self) -> bool:
        self.is_sleeping = not self.is_sleeping
        if self.is_sleeping:
            self.sfx.play("sleep")
            self.voice.stop()
        else:
            self.sfx.play("happy")
            self.voice.speak("Guten Morgen! Ausgeruht und voller Tatendrang! ☀️")
        return self.is_sleeping

    def get_next_appointment(self) -> Optional[Dict[str, Any]]:
        appointments = self.config.get("appointments", [])
        today_str = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")
        upcoming = [a for a in appointments if a.get("date") == today_str and a.get("time", "") >= now_time and not a.get("reminded", False)]
        if upcoming:
            upcoming.sort(key=lambda x: x.get("time", ""))
            return upcoming[0]
        return None


# ==============================================================================
# 9. EINSTELLUNGS- & HEALTH-DASHBOARD FENSTER
# ==============================================================================
class SettingsDialog(QDialog):
    """Modernes Cyberpunk/Dark Einstellungsmenü mit Health-Dashboard & Themes"""

    def __init__(self, config: ConfigManager, voice: VoiceEngine, llm: LLMEngine, tamagotchi: TamagotchiEngine, parent=None):
        super().__init__(parent)
        self.config = config
        self.voice = voice
        self.llm = llm
        self.tamagotchi = tamagotchi

        self.setWindowTitle("🐾 Yuyu Desktop Pet — Einstellungen & Dashboard")
        self.setMinimumSize(680, 560)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d121c;
                color: #e2e8f0;
                font-family: sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background-color: #070a10;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #111827;
                color: #94a3b8;
                padding: 9px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: #00d4ff;
                color: #040810;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #1e293b;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 14px;
                font-weight: bold;
                color: #00d4ff;
            }
            QLineEdit, QComboBox, QSpinBox, QTimeEdit, QDateEdit {
                background-color: #161e2e;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 10px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00d4ff;
            }
            QPushButton {
                background-color: #0284c7;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #00d4ff;
                color: #040810;
            }
            QTableWidget {
                background-color: #111827;
                border: 1px solid #1e293b;
                color: #e2e8f0;
                gridline-color: #1e293b;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #00d4ff;
                padding: 5px;
                font-weight: bold;
                border: none;
            }
            QProgressBar {
                border: 1px solid #1e293b;
                border-radius: 6px;
                text-align: center;
                background: #0f172a;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #00d4ff);
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._build_tab_dashboard()
        self._build_tab_llm()
        self._build_tab_voices()
        self._build_tab_tamagotchi()
        self._build_tab_appointments()
        self._build_tab_pomodoro()

        # Footer Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_save = QPushButton("💾 Speichern & Übernehmen")
        self.btn_save.clicked.connect(self._save_and_close)
        btn_box.addWidget(self.btn_save)

        self.btn_close = QPushButton("Schließen")
        self.btn_close.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_close)

        layout.addLayout(btn_box)

    def _build_tab_dashboard(self):
        tab = QWidget()
        l = QVBoxLayout(tab)

        lvl, title, xp = self.config.get_level_info()

        # RPG Level Box
        box_rpg = QGroupBox("⭐ Dein Tamagotchi Partner & Freundschafts-Level")
        br_l = QVBoxLayout(box_rpg)

        h_top = QHBoxLayout()
        lbl_avatar = QLabel("🐾")
        lbl_avatar.setStyleSheet("font-size: 38px; padding: 5px;")
        h_top.addWidget(lbl_avatar)

        v_meta = QVBoxLayout()
        v_meta.addWidget(QLabel(f"<b style='font-size:16px; color:#00d4ff;'>Level {lvl} — {title}</b>"))
        v_meta.addWidget(QLabel(f"<span style='color:#94a3b8;'>Gesamt Erfahrungspunkte: {xp} XP</span>"))
        h_top.addLayout(v_meta)
        h_top.addStretch()
        br_l.addLayout(h_top)

        # XP Fortschrittsbalken
        bar_xp = QProgressBar()
        bar_xp.setRange(0, 1000)
        bar_xp.setValue(min(1000, xp))
        bar_xp.setFormat(f"{xp} / 1000 XP bis Meisterschaft")
        br_l.addWidget(bar_xp)

        l.addWidget(box_rpg)

        # Tages-Gesundheits-Tracker
        box_health = QGroupBox("📊 Heutiger Gesundheits-Tracker (Tages-Statistiken)")
        bh_l = QVBoxLayout(box_health)

        prog = self.config.data.get("progression", {})
        stats = [
            ("🥤 Getrunkene Gläser Wasser:", f"{prog.get('water_drank_today', 0)} Gläser", "Empfohlen: 6-8 Gläser"),
            ("🥪 Zu sich genommene Mahlzeiten/Snacks:", f"{prog.get('meals_eaten_today', 0)} Mahlzeiten", "Regelmäßig essen"),
            ("🧘 Absolvierte Bildschirmpausen:", f"{prog.get('breaks_taken_today', 0)} Pausen", "Empfohlen: alle 45-60 Min"),
            ("🍅 Abgeschlossene Pomodoro-Phasen:", f"{prog.get('pomodoros_done_today', 0)} Sessions", "Fokussierte Arbeit"),
            ("🔥 Aktuelle Tages-Streak:", f"{prog.get('streak_days', 1)} Tage in Folge", "Bleib dran!")
        ]

        for title_str, val_str, sub in stats:
            h = QHBoxLayout()
            h.addWidget(QLabel(f"<b>{title_str}</b>"))
            lbl_v = QLabel(f"<span style='color:#00d4ff; font-weight:bold;'>{val_str}</span>")
            h.addWidget(lbl_v)
            h.addStretch()
            h.addWidget(QLabel(f"<span style='color:#64748b; font-size:10px;'>{sub}</span>"))
            bh_l.addLayout(h)

        l.addWidget(box_health)
        l.addStretch()

        self.tabs.addTab(tab, "📊 Dashboard & Level")

    def _build_tab_llm(self):
        tab = QWidget()
        l = QVBoxLayout(tab)

        box = QGroupBox("🤖 KI & LLM Provider (Freie Modellwahl)")
        box_l = QVBoxLayout(box)

        box_l.addWidget(QLabel("Wähle deinen Provider oder trage einfach einen API-Key ein (wird automatisch erkannt):"))

        h_prov = QHBoxLayout()
        h_prov.addWidget(QLabel("Provider:"))
        self.combo_provider = QComboBox()
        self.combo_provider.addItems([
            "Automatisch erkennen (Auto)",
            "Google Gemini (Direkt REST API)",
            "OpenAI (GPT-4o-mini / GPT-4o)",
            "Groq (Ultra-Fast Llama 3)",
            "OpenRouter (Multi-Model)",
            "Ollama / Lokales LLM",
            "Benutzerdefinierte Base-URL"
        ])
        h_prov.addWidget(self.combo_provider)
        box_l.addLayout(h_prov)

        h_key = QHBoxLayout()
        h_key.addWidget(QLabel("API-Key:"))
        self.txt_api_key = QLineEdit(self.config.get("api_key", ""))
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("Trage deinen API-Key ein (z.B. AIzaSy..., sk-..., gsk_...)")
        h_key.addWidget(self.txt_api_key)

        self.btn_show_key = QPushButton("👁️")
        self.btn_show_key.setFixedWidth(40)
        self.btn_show_key.clicked.connect(self._toggle_key_visibility)
        h_key.addWidget(self.btn_show_key)
        box_l.addLayout(h_key)

        h_model = QHBoxLayout()
        h_model.addWidget(QLabel("Modellname:"))
        self.txt_model = QLineEdit(self.config.get("model_name", "gemini-1.5-flash"))
        self.txt_model.setPlaceholderText("z.B. gemini-1.5-flash, gpt-4o-mini, llama-3.3-70b-versatile")
        h_model.addWidget(self.txt_model)
        box_l.addLayout(h_model)

        h_base = QHBoxLayout()
        h_base.addWidget(QLabel("Base-URL (Optional):"))
        self.txt_base_url = QLineEdit(self.config.get("base_url", ""))
        self.txt_base_url.setPlaceholderText("z.B. http://localhost:11434/v1 für Ollama")
        h_base.addWidget(self.txt_base_url)
        box_l.addLayout(h_base)

        self.btn_test_llm = QPushButton("⚡ API-Verbindung testen")
        self.btn_test_llm.clicked.connect(self._test_llm_connection)
        box_l.addWidget(self.btn_test_llm)

        self.lbl_llm_status = QLabel("")
        self.lbl_llm_status.setStyleSheet("font-weight: bold; padding: 4px;")
        box_l.addWidget(self.lbl_llm_status)

        l.addWidget(box)

        hint = QLabel(
            "💡 Hinweis: Falls kein API-Key eingetragen ist oder kein Internet besteht, "
            "nutzt das Pet ein umfangreiches deutsches Offline-Repertoire an frechen Sprüchen!"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #94a3b8; font-size: 11px;")
        l.addWidget(hint)
        l.addStretch()

        self.tabs.addTab(tab, "🤖 KI & API-Key")

    def _build_tab_voices(self):
        tab = QWidget()
        l = QVBoxLayout(tab)

        box = QGroupBox("🎙️ Die 4 Charakter-Stimmen")
        box_l = QVBoxLayout(box)

        self.voice_radios = {}
        curr_v = self.config.get("voice", "lola")

        for k, v in VOICES.items():
            h = QHBoxLayout()
            lbl = QLabel(f"<b>{v['name']}</b><br><span style='color:#94a3b8; font-size:11px;'>{v['description']}</span>")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            h.addWidget(lbl)

            btn_test = QPushButton("🔊 Anhören")
            btn_test.setFixedWidth(100)
            btn_test.clicked.connect(lambda ch, vk=k: self._test_voice(vk))
            h.addWidget(btn_test)

            btn_sel = QPushButton("Auswählen" if k != curr_v else "✓ Aktiv")
            btn_sel.setFixedWidth(100)
            if k == curr_v:
                btn_sel.setStyleSheet("background-color: #22c55e; color: black;")
            btn_sel.clicked.connect(lambda ch, vk=k: self._set_active_voice(vk))
            h.addWidget(btn_sel)
            self.voice_radios[k] = btn_sel

            box_l.addLayout(h)

        l.addWidget(box)

        box_audio = QGroupBox("🔊 Lautstärke & Audio")
        ba_l = QVBoxLayout(box_audio)

        h_vol = QHBoxLayout()
        h_vol.addWidget(QLabel("Lautstärke:"))
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(self.config.get("volume", 85))
        h_vol.addWidget(self.slider_vol)
        self.lbl_vol = QLabel(f"{self.slider_vol.value()}%")
        self.slider_vol.valueChanged.connect(lambda val: self.lbl_vol.setText(f"{val}%"))
        h_vol.addWidget(self.lbl_vol)
        ba_l.addLayout(h_vol)

        self.chk_mute = QCheckBox("Sprachausgabe komplett stummschalten (Mute)")
        self.chk_mute.setChecked(self.config.get("muted", False))
        ba_l.addWidget(self.chk_mute)

        l.addWidget(box_audio)
        l.addStretch()

        self.tabs.addTab(tab, "🎙️ 4 Stimmen")

    def _build_tab_tamagotchi(self):
        tab = QWidget()
        l = QVBoxLayout(tab)

        box_decay = QGroupBox("⏱️ Tamagotchi Intervalle (Zeit bis zum Notstand)")
        bd_l = QVBoxLayout(box_decay)

        decay = self.config.get("decay_minutes", {"hunger": 120, "thirst": 45, "energy": 50})

        h_t = QHBoxLayout()
        h_t.addWidget(QLabel("💧 Durst-Intervall (Wasser trinken):"))
        self.spn_thirst = QSpinBox()
        self.spn_thirst.setRange(10, 240)
        self.spn_thirst.setValue(decay.get("thirst", 45))
        self.spn_thirst.setSuffix(" Min")
        h_t.addWidget(self.spn_thirst)
        bd_l.addLayout(h_t)

        h_e = QHBoxLayout()
        h_e.addWidget(QLabel("⚡ Pausen-Intervall (Bildschirmpause / Dehnen):"))
        self.spn_energy = QSpinBox()
        self.spn_energy.setRange(10, 180)
        self.spn_energy.setValue(decay.get("energy", 50))
        self.spn_energy.setSuffix(" Min")
        h_e.addWidget(self.spn_energy)
        bd_l.addLayout(h_e)

        h_h = QHBoxLayout()
        h_h.addWidget(QLabel("🥪 Hunger-Intervall (Essen / Snack):"))
        self.spn_hunger = QSpinBox()
        self.spn_hunger.setRange(20, 360)
        self.spn_hunger.setValue(decay.get("hunger", 120))
        self.spn_hunger.setSuffix(" Min")
        h_h.addWidget(self.spn_hunger)
        bd_l.addLayout(h_h)

        l.addWidget(box_decay)

        box_nag = QGroupBox("😼 Die kleine Nervensäge & HUD Styling")
        bn_l = QVBoxLayout(box_nag)

        h_int = QHBoxLayout()
        h_int.addWidget(QLabel("Nerv-Intensität:"))
        self.combo_intensity = QComboBox()
        self.combo_intensity.addItems(["Sanfte Erinnerung", "Frecher Begleiter (Standard)", "Extreme Nervensäge"])
        cur_int = self.config.get("nag_intensity", "frech")
        idx = 0 if cur_int == "sanft" else (2 if cur_int == "extrem" else 1)
        self.combo_intensity.setCurrentIndex(idx)
        h_int.addWidget(self.combo_intensity)
        bn_l.addLayout(h_int)

        h_thm = QHBoxLayout()
        h_thm.addWidget(QLabel("HUD Design / Theme:"))
        self.combo_theme = QComboBox()
        for tk, tv in HUD_THEMES.items():
            self.combo_theme.addItem(tv["name"], tk)
        cur_thm = self.config.get("hud_theme", "cyberpunk")
        idx_t = list(HUD_THEMES.keys()).index(cur_thm) if cur_thm in HUD_THEMES else 0
        self.combo_theme.setCurrentIndex(idx_t)
        h_thm.addWidget(self.combo_theme)
        bn_l.addLayout(h_thm)

        self.chk_hud = QCheckBox("Tamagotchi-Statusleiste (🥪 💧 ⚡) über dem Pet anzeigen")
        self.chk_hud.setChecked(self.config.get("show_tamagotchi_hud", True))
        bn_l.addWidget(self.chk_hud)

        self.chk_roam = QCheckBox("Selbstständig auf dem Desktop wandern (Roaming)")
        self.chk_roam.setChecked(self.config.get("roaming_enabled", True))
        bn_l.addWidget(self.chk_roam)

        l.addWidget(box_nag)
        l.addStretch()

        self.tabs.addTab(tab, "🐾 Tamagotchi & Themes")

    def _build_tab_appointments(self):
        tab = QWidget()
        l = QVBoxLayout(tab)

        box_add = QGroupBox("➕ Neuen Termin / Erinnerung hinzufügen")
        ba_l = QVBoxLayout(box_add)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Titel / Aufgabe:"))
        self.txt_app_title = QLineEdit()
        self.txt_app_title.setPlaceholderText("z.B. Team-Meeting, Backofen ausmachen, Arzttermin")
        h1.addWidget(self.txt_app_title)
        ba_l.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Datum:"))
        self.date_app = QDateEdit(QDate.currentDate())
        self.date_app.setCalendarPopup(True)
        h2.addWidget(self.date_app)

        h2.addWidget(QLabel("Uhrzeit:"))
        self.time_app = QTimeEdit(QTime.currentTime().addSecs(1800))
        h2.addWidget(self.time_app)

        self.btn_add_app = QPushButton("Termin speichern")
        self.btn_add_app.clicked.connect(self._add_appointment)
        h2.addWidget(self.btn_add_app)
        ba_l.addLayout(h2)

        l.addWidget(box_add)

        self.table_apps = QTableWidget(0, 4)
        self.table_apps.setHorizontalHeaderLabels(["Datum", "Uhrzeit", "Termin", "Aktion"])
        self.table_apps.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        l.addWidget(self.table_apps)

        self._refresh_appointments_table()
        self.tabs.addTab(tab, "📅 Termine")

    def _build_tab_pomodoro(self):
        tab = QWidget()
        l = QVBoxLayout(tab)

        box = QGroupBox("🍅 Pomodoro Fokus-Trainer")
        b_l = QVBoxLayout(box)

        b_l.addWidget(QLabel("Strukturiertes Arbeiten mit 25 Minuten Fokus und 5 Minuten Pause:"))

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Fokus-Dauer (Minuten):"))
        self.spn_pomo_focus = QSpinBox()
        self.spn_pomo_focus.setRange(5, 60)
        self.spn_pomo_focus.setValue(25)
        h1.addWidget(self.spn_pomo_focus)
        b_l.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Pausen-Dauer (Minuten):"))
        self.spn_pomo_break = QSpinBox()
        self.spn_pomo_break.setRange(2, 30)
        self.spn_pomo_break.setValue(5)
        h2.addWidget(self.spn_pomo_break)
        b_l.addLayout(h2)

        info = QLabel(
            "💡 Du kannst den Pomodoro-Timer jederzeit mit Rechtsklick auf das Pet starten!\n"
            "Das Pet unterstützt dich während der Arbeitsphase und erinnert dich pünktlich an die Pause."
        )
        info.setStyleSheet("color: #94a3b8; font-size: 11px;")
        b_l.addWidget(info)

        l.addWidget(box)
        l.addStretch()

        self.tabs.addTab(tab, "🍅 Pomodoro")

    def _refresh_appointments_table(self):
        apps = self.config.get("appointments", [])
        self.table_apps.setRowCount(len(apps))
        for row, a in enumerate(apps):
            self.table_apps.setItem(row, 0, QTableWidgetItem(a.get("date", "")))
            self.table_apps.setItem(row, 1, QTableWidgetItem(a.get("time", "")))
            self.table_apps.setItem(row, 2, QTableWidgetItem(a.get("title", "")))

            btn_del = QPushButton("❌")
            btn_del.setFixedWidth(40)
            btn_del.clicked.connect(lambda ch, r=row: self._delete_appointment(r))
            self.table_apps.setCellWidget(row, 3, btn_del)

    def _add_appointment(self):
        title = self.txt_app_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Fehler", "Bitte einen Titel eingeben!")
            return
        d_str = self.date_app.date().toString("yyyy-MM-dd")
        t_str = self.time_app.time().toString("HH:mm")

        apps = list(self.config.get("appointments", []))
        apps.append({
            "id": f"app_{int(time.time()*1000)}",
            "title": title,
            "date": d_str,
            "time": t_str,
            "reminded": False
        })
        self.config.set("appointments", apps)
        self.txt_app_title.clear()
        self._refresh_appointments_table()

    def _delete_appointment(self, row: int):
        apps = list(self.config.get("appointments", []))
        if 0 <= row < len(apps):
            apps.pop(row)
            self.config.set("appointments", apps)
            self._refresh_appointments_table()

    def _toggle_key_visibility(self):
        if self.txt_api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_show_key.setText("🔒")
        else:
            self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_show_key.setText("👁️")

    def _test_voice(self, voice_key: str):
        test_phrases = {
            "lola": "Huhu! Ich bin Lola! Wach auf, Operator, Zeit für Action!",
            "buster": "Hey! Buster hier. Sitzt du immer noch vor dem Bildschirm? Mach mal hinne!",
            "mimi": "Hallo mein Lieber. Mimi hier. Vergiss bitte nicht, genug Wasser zu trinken!",
            "klaus": "Tach. Klaus am Apparat. Kein langes Reden: Pause machen, sonst Feierabend."
        }
        phrase = test_phrases.get(voice_key, "Hallo! Test der Sprachausgabe!")
        self.voice.speak(phrase, voice_override=voice_key)

    def _set_active_voice(self, voice_key: str):
        self.config.set("voice", voice_key)
        for k, btn in self.voice_radios.items():
            if k == voice_key:
                btn.setText("✓ Aktiv")
                btn.setStyleSheet("background-color: #22c55e; color: black;")
            else:
                btn.setText("Auswählen")
                btn.setStyleSheet("")
        self._test_voice(voice_key)

    def _test_llm_connection(self):
        key = self.txt_api_key.text().strip()
        if not key:
            self.lbl_llm_status.setText("❌ Bitte zuerst einen API-Key eintragen!")
            self.lbl_llm_status.setStyleSheet("color: #ef4444; font-weight: bold;")
            return

        self.lbl_llm_status.setText("⏳ Teste Verbindung zum LLM...")
        self.lbl_llm_status.setStyleSheet("color: #eab308; font-weight: bold;")
        QApplication.processEvents()

        self.config.data["api_key"] = key
        self.config.data["model_name"] = self.txt_model.text().strip() or "gemini-1.5-flash"
        self.config.data["base_url"] = self.txt_base_url.text().strip()

        threading.Thread(target=self._run_llm_test, daemon=True).start()

    def _run_llm_test(self):
        try:
            res = self.llm.generate_nag("thirst", "Testverbindung")
            QTimer.singleShot(0, lambda: self._on_llm_test_success(res))
        except Exception as e:
            QTimer.singleShot(0, lambda: self._on_llm_test_fail(str(e)))

    def _on_llm_test_success(self, res: str):
        self.lbl_llm_status.setText(f"✓ Verbunden! Antwort: „{res}“")
        self.lbl_llm_status.setStyleSheet("color: #22c55e; font-weight: bold;")

    def _on_llm_test_fail(self, err: str):
        self.lbl_llm_status.setText(f"❌ Verbindungsfehler: {err}")
        self.lbl_llm_status.setStyleSheet("color: #ef4444; font-weight: bold;")

    def _save_and_close(self):
        self.config.data["api_key"] = self.txt_api_key.text().strip()
        self.config.data["model_name"] = self.txt_model.text().strip() or "gemini-1.5-flash"
        self.config.data["base_url"] = self.txt_base_url.text().strip()
        self.config.data["volume"] = self.slider_vol.value()
        self.config.data["muted"] = self.chk_mute.isChecked()
        self.config.data["show_tamagotchi_hud"] = self.chk_hud.isChecked()
        self.config.data["roaming_enabled"] = self.chk_roam.isChecked()
        self.config.data["hud_theme"] = self.combo_theme.currentData()

        idx = self.combo_intensity.currentIndex()
        self.config.data["nag_intensity"] = "sanft" if idx == 0 else ("extrem" if idx == 2 else "frech")

        self.config.data["decay_minutes"] = {
            "thirst": self.spn_thirst.value(),
            "energy": self.spn_energy.value(),
            "hunger": self.spn_hunger.value()
        }

        self.config.save()
        self.accept()


# ==============================================================================
# 10. HAUPTFENSTER: DESKTOP PET & TAMAGOTCHI OVERLAY
# ==============================================================================
class DesktopPetWindow(QWidget):
    """Natives PyQt6 Desktop-Overlay mit Anti-Aliasing, Ball-Spiel, Pomodoro & Themes"""

    def __init__(self, config: ConfigManager, voice: VoiceEngine, llm: LLMEngine, tamagotchi: TamagotchiEngine, sfx: RetroSoundSynthesizer):
        super().__init__()
        self.config = config
        self.voice = voice
        self.llm = llm
        self.tamagotchi = tamagotchi
        self.sfx = sfx

        # Fenster-Flags: Transparent, rahmenlos, immer im Vordergrund
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # Spritesheet laden
        self.spritesheet = None
        self._load_spritesheet()

        # Skalierung & Rendering
        self.scale = float(self.config.get("scale", 0.70))
        self.hud_height = 58
        self._update_window_size()

        # Animation State
        self.current_anim = "idle"
        self.frame_idx = 0
        self.anim_start_time = time.time()
        self.gaze_dir = 0
        self.gaze_tracking_enabled = True

        # Autonomes Roaming
        self.roam_direction = "idle"
        self.roam_end_time = 0.0
        self.next_roam_decision = time.time() + 2.0

        # Drag & Drop Handling
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.drag_moved_threshold = False

        # Partikel & Spiele
        self.particles: List[Particle] = []
        self.ball_game = BallGame()
        self.pomodoro = PomodoroManager()

        # Sprechblase & Audio Bounce
        self.speech_bubble_text = ""
        self.speech_bubble_timeout = 0.0
        self.audio_level = 0.0

        # Signale verbinden
        self.voice.speech_started.connect(self._on_speech_started)
        self.voice.audio_level.connect(self._on_audio_level)
        self.tamagotchi.nag_triggered.connect(self._on_nag_triggered)
        self.tamagotchi.vitals_updated.connect(lambda v: self.update())
        self.tamagotchi.level_up.connect(self._on_level_up)
        self.pomodoro.tick.connect(self._on_pomodoro_tick)
        self.pomodoro.finished.connect(self._on_pomodoro_finished)

        # 60 FPS Game Loop Timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._game_loop)
        self.anim_timer.start(16)

        # Initiale Positionierung am unteren Bildschirmrand
        self._initial_placement()

        # System Tray Icon (KDE Plasma Taskleiste)
        self._init_tray_icon()

    def _load_spritesheet(self):
        script_dir = Path(__file__).resolve().parent
        candidate_paths = [
            script_dir / "pets" / "yuyu-chibi" / "spritesheet.webp",
            Path.home() / ".local" / "share" / "webjarvis_petaddon" / "pets" / "yuyu-chibi" / "spritesheet.webp",
            Path("/home/graba/Downloads/driver-and tools/yuyu-chibi/spritesheet.webp")
        ]
        chosen = next((p for p in candidate_paths if p.exists()), None)
        if chosen:
            self.spritesheet = QImage(str(chosen))
            print(f"[DesktopPet] Spritesheet geladen: {chosen} ({self.spritesheet.width()}x{self.spritesheet.height()})")

    def _update_window_size(self):
        w = int(FRAME_WIDTH * self.scale) + 40
        h = int(FRAME_HEIGHT * self.scale) + self.hud_height + 40
        self.setFixedSize(w, h)

    def _initial_placement(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            saved_x = self.config.get("pos_x", -1)
            saved_y = self.config.get("pos_y", -1)
            if saved_x > 0 and saved_y > 0 and saved_x < geom.right() - 50:
                self.move(saved_x, saved_y)
            else:
                x = geom.right() - self.width() - 80
                y = geom.bottom() - self.height() - 10
                self.move(x, y)

    def _init_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(icon_pixmap)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.spritesheet and not self.spritesheet.isNull():
            crop = self.spritesheet.copy(0, 0, FRAME_WIDTH, FRAME_HEIGHT)
            scaled = crop.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            p.drawImage(0, 0, scaled)
        else:
            p.setBrush(QColor(0, 212, 255))
            p.drawEllipse(2, 2, 28, 28)
        p.end()

        self.tray_icon = QSystemTrayIcon(QIcon(icon_pixmap), self)
        self.tray_icon.setToolTip("🐾 Yuyu Desktop Pet & Tamagotchi")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu { background-color: #0f172a; color: #e2e8f0; border: 1px solid #00d4ff; border-radius: 6px; padding: 4px; }
            QMenu::item { padding: 5px 18px; border-radius: 4px; }
            QMenu::item:selected { background-color: #00d4ff; color: #040810; font-weight: bold; }
        """)

        act_vis = tray_menu.addAction("👁️ Pet Einblenden / Verstecken")
        act_vis.triggered.connect(self._toggle_visibility)

        tray_menu.addSeparator()

        tray_menu.addAction("🥪 Snack füttern").triggered.connect(lambda: self._feed_snack_action("sandwich"))
        tray_menu.addAction("🥤 Wasser trinken").triggered.connect(lambda: self._feed_snack_action("water"))
        tray_menu.addAction("🧘 Pause machen").triggered.connect(self._take_break_action)

        tray_menu.addSeparator()

        tray_menu.addAction("⚙️ Einstellungen & Dashboard...").triggered.connect(self._open_settings)
        tray_menu.addAction("❌ Beenden").triggered.connect(self._exit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_visibility()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            step = 0.05 if delta > 0 else -0.05
            new_scale = max(0.35, min(1.30, round(self.scale + step, 2)))
            self._set_scale(new_scale)
            self.speech_bubble_text = f"Größe: {int(new_scale * 100)}%"
            self.speech_bubble_timeout = time.time() + 1.5
            event.accept()
        else:
            super().wheelEvent(event)

    def add_particle(self, text: str, color: QColor, offset_x: float = 0.0, offset_y: float = 0.0):
        cx = self.width() // 2 + offset_x
        cy = self.hud_height + 25 + offset_y
        vx = random.uniform(-0.6, 0.6)
        vy = random.uniform(-1.8, -0.9)
        self.particles.append(Particle(cx, cy, text, color, vx, vy, max_life=2.0))

    def _game_loop(self):
        now = time.time()

        # 1. Partikel updaten
        self.particles = [p for p in self.particles if p.update()]

        # Zzz Partikel im Schlafmodus
        if self.tamagotchi.is_sleeping and random.random() < 0.035:
            self.add_particle("Zzz...", QColor(96, 165, 250), offset_x=random.uniform(-15, 15))

        # 2. Ball-Fangspiel Physik & Pet-Tracking
        if self.ball_game.active:
            ground_y = self.height() - 25
            self.ball_game.update_physics(ground_y)

            # Pet läuft dem Ball hinterher
            ball_local_x = self.ball_game.x
            pet_center_x = self.width() // 2

            if not self.ball_game.target_caught:
                dist = ball_local_x - pet_center_x
                if abs(dist) > 20:
                    if dist > 0:
                        self.current_anim = "running-right"
                        self.move(self.x() + 3, self.y())
                    else:
                        self.current_anim = "running-left"
                        self.move(self.x() - 3, self.y())
                else:
                    # Ball gefangen!
                    self.ball_game.target_caught = True
                    self.ball_game.active = False
                    self.current_anim = "jumping"
                    self.anim_start_time = now
                    self.sfx.play("ball_catch")
                    self.add_particle("⭐", QColor(250, 204, 21))
                    self.add_particle("🎾", QColor(163, 230, 53), offset_y=-10)
                    self.config.add_xp(15)
                    self.voice.speak("Hab ihn gefangen! Das war ein Riesenspaß! 🎾✨")

        # 3. Gaze Tracking
        elif self.gaze_tracking_enabled and self.current_anim == "idle" and not self.tamagotchi.is_sleeping:
            cursor_pos = QCursor.pos()
            pet_center = self.mapToGlobal(QPoint(self.width() // 2, self.height() // 2))
            dx = cursor_pos.x() - pet_center.x()
            dy = cursor_pos.y() - pet_center.y()

            if math.hypot(dx, dy) > 35:
                angle = (math.atan2(dy, dx) * 180.0 / math.pi) % 360.0
                sector = int((angle + 11.25) / 22.5) % 16
                self.gaze_dir = sector
            else:
                self.gaze_dir = 0
        else:
            self.gaze_dir = 0

        # 4. Animations-Frame berechnen
        anim_cfg = ANIMATIONS.get(self.current_anim, ANIMATIONS["idle"])
        elapsed_ms = int((now - self.anim_start_time) * 1000)

        if anim_cfg["loop"]:
            total_dur = anim_cfg["duration_ms"]
            self.frame_idx = int((elapsed_ms % total_dur) / (total_dur / anim_cfg["frames"]))
        else:
            total_dur = anim_cfg["duration_ms"]
            if elapsed_ms >= total_dur:
                self.current_anim = "idle"
                self.anim_start_time = now
                self.frame_idx = 0
            else:
                self.frame_idx = min(anim_cfg["frames"] - 1, int(elapsed_ms / (total_dur / anim_cfg["frames"])))

        # 5. Autonomes Roaming (nur wenn wach und kein Ball im Spiel)
        if self.config.get("roaming_enabled", True) and not self.is_dragging and not self.ball_game.active and not self.tamagotchi.is_sleeping:
            if now > self.next_roam_decision:
                choice = random.random()
                if choice < 0.35:
                    self.roam_direction = "left"
                    self.current_anim = "running-left"
                    self.roam_end_time = now + random.uniform(2.5, 4.5)
                elif choice < 0.70:
                    self.roam_direction = "right"
                    self.current_anim = "running-right"
                    self.roam_end_time = now + random.uniform(2.5, 4.5)
                else:
                    self.roam_direction = "idle"
                    self.current_anim = "idle"
                    self.roam_end_time = now + random.uniform(3.0, 7.0)

                self.anim_start_time = now
                self.next_roam_decision = self.roam_end_time + random.uniform(3.0, 6.0)

            if now < self.roam_end_time and self.roam_direction != "idle":
                screen = self.screen() or QApplication.primaryScreen()
                if screen:
                    geom = screen.availableGeometry()
                    speed = 2
                    cur_x = self.x()

                    if self.roam_direction == "left":
                        new_x = cur_x - speed
                        if new_x < geom.left() + 20:
                            self.roam_direction = "right"
                            self.current_anim = "running-right"
                            self.anim_start_time = now
                        else:
                            self.move(new_x, self.y())
                    elif self.roam_direction == "right":
                        new_x = cur_x + speed
                        if new_x + self.width() > geom.right() - 20:
                            self.roam_direction = "left"
                            self.current_anim = "running-left"
                            self.anim_start_time = now
                        else:
                            self.move(new_x, self.y())
            elif now >= self.roam_end_time and self.current_anim.startswith("running"):
                self.current_anim = "idle"
                self.anim_start_time = now

        self.update()

    def _on_speech_started(self, text: str):
        self.speech_bubble_text = text
        self.speech_bubble_timeout = time.time() + max(3.5, len(text) * 0.065)

    def _on_audio_level(self, lvl: float):
        self.audio_level = lvl

    def _on_nag_triggered(self, vital_type: str, text: str):
        self.speech_bubble_text = text
        self.speech_bubble_timeout = time.time() + 5.0
        self.current_anim = "jumping"
        self.anim_start_time = time.time()

    def _on_level_up(self, lvl: int, title: str):
        for _ in range(8):
            self.add_particle("⭐", QColor(250, 204, 21), offset_x=random.uniform(-25, 25))
        self.speech_bubble_text = f"LEVEL UP! Level {lvl} ({title})! 🎉"
        self.speech_bubble_timeout = time.time() + 4.5
        self.current_anim = "jumping"

    def _on_pomodoro_tick(self, mode: str, secs: int):
        self.update()

    def _on_pomodoro_finished(self, completed_mode: str):
        if completed_mode == "FOCUS":
            self.sfx.play("level_up")
            self.voice.speak("Pomodoro-Fokus vollendet! Große Klasse! Jetzt 5 Minuten Pause machen! ☕")
            self.config.add_xp(50)
            prog = self.config.data.setdefault("progression", {})
            prog["pomodoros_done_today"] = prog.get("pomodoros_done_today", 0) + 1
            self.config.save()
            for _ in range(6):
                self.add_particle("🍅", QColor(239, 68, 68))
        else:
            self.sfx.play("happy")
            self.voice.speak("Pause beendet! Bereit für die nächste Runde!")

    # ==========================================================================
    # PAINTING & RENDERING (ANTI-ALIASED SMOOTH TRANSFORMATION)
    # ==========================================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        now = time.time()

        # 1. Tamagotchi HUD über dem Pet zeichnen
        if self.config.get("show_tamagotchi_hud", True):
            self._draw_tamagotchi_hud(painter)

        # 2. Sprechblase zeichnen
        if self.speech_bubble_text and now < self.speech_bubble_timeout and not self.tamagotchi.is_sleeping:
            self._draw_speech_bubble(painter)

        # 3. Haftnotiz (Sticky Note) zeichnen
        note = self.config.get("sticky_note", "")
        if note and not self.tamagotchi.is_sleeping and (not self.speech_bubble_text or now >= self.speech_bubble_timeout):
            self._draw_sticky_note(painter, note)

        # 4. Tennisball zeichnen
        if self.ball_game.active:
            painter.setPen(QPen(QColor(163, 230, 53), 1.5))
            painter.setBrush(QColor(190, 242, 100))
            painter.drawEllipse(int(self.ball_game.x - 7), int(self.ball_game.y - 7), 14, 14)

        # 4. Pet Sprite bilinearglättend rendern
        if self.spritesheet and not self.spritesheet.isNull():
            anim_cfg = ANIMATIONS.get(self.current_anim, ANIMATIONS["idle"])
            row = anim_cfg["row"]
            col = self.frame_idx % anim_cfg["frames"]

            src_x = col * FRAME_WIDTH
            src_y = row * FRAME_HEIGHT

            gaze_off_x = 0
            gaze_off_y = 0
            if self.gaze_dir > 0 and self.current_anim == "idle":
                rad = self.gaze_dir * (22.5 * math.pi / 180.0)
                gaze_off_x = int(math.cos(rad) * 4)
                gaze_off_y = int(math.sin(rad) * 3)

            bounce_y = int(self.audio_level * -8.0) if self.voice.is_speaking() else 0

            dst_w = int(FRAME_WIDTH * self.scale)
            dst_h = int(FRAME_HEIGHT * self.scale)
            dst_x = (self.width() - dst_w) // 2 + gaze_off_x
            dst_y = self.hud_height + 25 + bounce_y + gaze_off_y

            frame_crop = self.spritesheet.copy(src_x, src_y, FRAME_WIDTH, FRAME_HEIGHT)
            scaled_frame = frame_crop.scaled(
                dst_w, dst_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Schatten
            shadow_rect = QRectF(dst_x + 10, dst_y + dst_h - 10, dst_w - 20, 10)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 75))
            painter.drawEllipse(shadow_rect)

            # Wenn schlafend: leicht abgedunkelt
            if self.tamagotchi.is_sleeping:
                painter.setOpacity(0.85)

            painter.drawImage(dst_x, dst_y, scaled_frame)
            painter.setOpacity(1.0)

        # 5. Schwebende Partikel zeichnen
        for p in self.particles:
            alpha = int(p.alpha() * 255)
            if alpha > 0:
                col = QColor(p.color)
                col.setAlpha(alpha)
                painter.setPen(col)
                painter.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
                painter.drawText(int(p.x), int(p.y), p.text)

    def _draw_tamagotchi_hud(self, painter: QPainter):
        hud_w = self.width() - 10
        hud_h = 48
        hud_x = 5
        hud_y = 5

        thm_key = self.config.get("hud_theme", "cyberpunk")
        theme = HUD_THEMES.get(thm_key, HUD_THEMES["cyberpunk"])

        # Hintergrund-Pille mit Theme-Farbe
        painter.setPen(QPen(theme["border"], 1.2))
        painter.setBrush(theme["bg"])
        painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 8, 8)

        # Schlafmodus-Anzeige
        if self.tamagotchi.is_sleeping:
            painter.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))
            painter.setPen(QColor(147, 197, 253))
            painter.drawText(QRect(hud_x, hud_y + 12, hud_w, 20), Qt.AlignmentFlag.AlignCenter, "💤 Schläft tief und fest (DND)")
            return

        # 3 Mini-Balken: 🥪 Hunger, 💧 Durst, ⚡ Energie
        vitals = [
            ("🥪", self.tamagotchi.hunger, theme["hunger"]),
            ("💧", self.tamagotchi.thirst, theme["thirst"]),
            ("⚡", self.tamagotchi.energy, theme["energy"])
        ]

        bar_w = (hud_w - 24) // 3
        bar_h = 5
        painter.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))

        for i, (icon, val, base_color) in enumerate(vitals):
            bx = hud_x + 6 + i * (bar_w + 6)
            by = hud_y + 5

            painter.setPen(theme["text"])
            painter.drawText(bx, by + 12, f"{icon} {int(val)}%")

            bar_y = by + 17
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(30, 41, 59, 180))
            painter.drawRoundedRect(bx, bar_y, bar_w, bar_h, 2, 2)

            fill_color = base_color
            if val < 25.0:
                fill_color = QColor(239, 68, 68)
            elif val < 50.0:
                fill_color = QColor(234, 179, 8)

            fill_w = max(2, int((bar_w * val) / 100.0))
            painter.setBrush(fill_color)
            painter.drawRoundedRect(bx, bar_y, fill_w, bar_h, 2, 2)

        # Untere Info-Zeile: Pomodoro / Termine / Level
        painter.setFont(QFont("sans-serif", 7))
        if self.pomodoro.mode != "OFF":
            mins = self.pomodoro.seconds_left // 60
            secs = self.pomodoro.seconds_left % 60
            badge = "🍅 Fokus" if self.pomodoro.mode == "FOCUS" else "☕ Pause"
            pomo_str = f"{badge}: {mins:02d}:{secs:02d}"
            painter.setPen(QColor(239, 68, 68) if self.pomodoro.mode == "FOCUS" else QColor(34, 197, 94))
            painter.drawText(hud_x + 8, hud_y + 42, pomo_str)
        else:
            next_app = self.tamagotchi.get_next_appointment()
            if next_app:
                t_str = f"📅 {next_app.get('time')}: {next_app.get('title')}"
                painter.setPen(theme["accent"])
                painter.drawText(hud_x + 8, hud_y + 42, t_str[:30])
            else:
                lvl, tit, _ = self.config.get_level_info()
                painter.setPen(QColor(148, 163, 184, 200))
                painter.drawText(hud_x + 8, hud_y + 42, f"⭐ Lv. {lvl} {tit}")

    def _draw_speech_bubble(self, painter: QPainter):
        text = self.speech_bubble_text
        painter.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))

        bubble_w = min(self.width() + 40, 220)
        bubble_x = (self.width() - bubble_w) // 2
        bubble_y = self.hud_height + 4

        metrics = painter.fontMetrics()
        rect = metrics.boundingRect(QRect(0, 0, bubble_w - 16, 200), Qt.TextFlag.TextWordWrap, text)
        bubble_h = rect.height() + 14

        painter.setPen(QPen(QColor(0, 212, 255, 180), 1.5))
        painter.setBrush(QColor(15, 23, 42, 240))
        painter.drawRoundedRect(bubble_x, bubble_y, bubble_w, bubble_h, 10, 10)

        painter.setPen(QColor(255, 255, 255))
        text_rect = QRect(bubble_x + 8, bubble_y + 6, bubble_w - 16, bubble_h - 10)
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, text)

    def _draw_sticky_note(self, painter: QPainter, note: str):
        painter.setFont(QFont("sans-serif", 7, QFont.Weight.Bold))
        note_text = f"📝 {note}"
        metrics = painter.fontMetrics()
        w = min(self.width() - 8, metrics.horizontalAdvance(note_text) + 14)
        h = 20
        x = (self.width() - w) // 2
        y = self.hud_height + 6

        # Gelbe Haftnotiz Optik
        painter.setPen(QPen(QColor(234, 179, 8, 200), 1))
        painter.setBrush(QColor(254, 240, 138, 230))
        painter.drawRoundedRect(x, y, w, h, 4, 4)

        painter.setPen(QColor(113, 63, 18))
        rect = QRect(x + 4, y + 2, w - 8, h - 4)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine, metrics.elidedText(note_text, Qt.TextElideMode.ElideRight, w - 8))

    def _edit_sticky_note(self):
        cur_note = self.config.get("sticky_note", "")
        text, ok = QInputDialog.getText(
            self, "📝 Desktop Haftnotiz",
            "Text für die Haftnotiz (leer lassen zum Löschen):",
            text=cur_note
        )
        if ok:
            self.config.set("sticky_note", text.strip())
            if text.strip():
                self.speech_bubble_text = "Haftnotiz angeheftet! 📝"
                self.sfx.play("happy")
            else:
                self.speech_bubble_text = "Haftnotiz entfernt!"
            self.speech_bubble_timeout = time.time() + 2.5
            self.update()

    # ==========================================================================
    # MAUS & DRAG & DROP HANDLING
    # ==========================================================================
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.drag_moved_threshold = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            new_pos = event.globalPosition().toPoint() - self.drag_start_pos
            self.move(new_pos)
            self.drag_moved_threshold = True
            self.current_anim = "jumping"
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            if self.drag_moved_threshold:
                self.config.set("pos_x", self.x())
                self.config.set("pos_y", self.y())
                drag_line = random.choice(OFFLINE_NAG_LINES["drag"])
                self.speech_bubble_text = drag_line
                self.speech_bubble_timeout = time.time() + 4.0
                self.voice.speak(drag_line)
            else:
                if self.tamagotchi.is_sleeping:
                    self.tamagotchi.toggle_sleep()
                else:
                    click_line = random.choice(OFFLINE_NAG_LINES["click"])
                    self.speech_bubble_text = click_line
                    self.speech_bubble_timeout = time.time() + 3.0
                    self.current_anim = "waving"
                    self.anim_start_time = time.time()
                    self.sfx.play("happy")
                    self.add_particle("❤️", QColor(244, 63, 94))
                    self.config.add_xp(5)
                    self.voice.speak(click_line)
            event.accept()

    # ==========================================================================
    # RECHTSKLICK KONTEXTMENÜ
    # ==========================================================================
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #00d4ff;
                border-radius: 8px;
                padding: 6px;
                font-family: sans-serif;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00d4ff;
                color: #050b14;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background: #334155;
                margin: 4px 6px;
            }
        """)

        # 1. Snack-Bar & Füttern Submenü
        snack_menu = menu.addMenu("🍽️ Snack-Bar & Füttern")
        snack_menu.addAction("🥪 Sandwich / Mahlzeit (+50% Hunger)").triggered.connect(lambda: self._feed_snack_action("sandwich"))
        snack_menu.addAction("🍎 Knackiger Apfel (+25% Hunger, +10% Vitalität)").triggered.connect(lambda: self._feed_snack_action("apple"))
        snack_menu.addAction("☕ Heißer Kaffee / Espresso (+40% Energie-Boost)").triggered.connect(lambda: self._feed_snack_action("coffee"))
        snack_menu.addAction("🥤 Frisches Glas Wasser (+50% Hydration)").triggered.connect(lambda: self._feed_snack_action("water"))
        snack_menu.addAction("🍩 Süßer Donut (+30% Hunger, +10 Zuneigung)").triggered.connect(lambda: self._feed_snack_action("donut"))

        act_break = menu.addAction("🧘 Bildschirmpause machen & Dehnen (+100%)")
        act_break.triggered.connect(self._take_break_action)

        menu.addSeparator()

        # 2. Interaktives Ballspiel
        act_ball = menu.addAction("🎾 Ball werfen (Fangspiel)")
        act_ball.triggered.connect(self._throw_ball_action)

        # 3. Pomodoro Fokus
        if self.pomodoro.mode == "OFF":
            act_pomo = menu.addAction("🍅 Pomodoro Fokus starten (25 Min)")
            act_pomo.triggered.connect(lambda: self.pomodoro.start_focus(25))
        else:
            act_pomo = menu.addAction(f"⏹️ Pomodoro stoppen ({self.pomodoro.seconds_left // 60}m verbleibend)")
            act_pomo.triggered.connect(self.pomodoro.stop)

        # 4. Schlaf- & Nachtmodus (DND)
        sleep_text = "⏰ Aufwecken" if self.tamagotchi.is_sleeping else "💤 Schlafen legen (Zzz... DND)"
        act_sleep = menu.addAction(sleep_text)
        act_sleep.triggered.connect(self._toggle_sleep_action)

        # 5. Haftnotiz (Sticky Note)
        cur_note = self.config.get("sticky_note", "")
        note_text = f"📝 Haftnotiz bearbeiten ({cur_note[:12]}...)" if cur_note else "📝 Haftnotiz anheften (Memo)..."
        act_note = menu.addAction(note_text)
        act_note.triggered.connect(self._edit_sticky_note)

        menu.addSeparator()

        # 5. Stimmen-Submenü (4 Stimmen)
        voice_menu = menu.addMenu("🎙️ Stimme auswählen")
        cur_v = self.config.get("voice", "lola")
        for k, v in VOICES.items():
            act_v = voice_menu.addAction(f"{'✓ ' if k == cur_v else ''}{v['name']}")
            act_v.triggered.connect(lambda ch, vk=k: self._change_voice_quick(vk))

        # 6. Themes Submenü
        theme_menu = menu.addMenu("🎨 HUD-Theme")
        cur_t = self.config.get("hud_theme", "cyberpunk")
        for tk, tv in HUD_THEMES.items():
            act_t = theme_menu.addAction(f"{'✓ ' if tk == cur_t else ''}{tv['name']}")
            act_t.triggered.connect(lambda ch, thk=tk: self._set_theme(thk))

        # 7. Tamagotchi HUD Toggle & Roaming
        hud_text = "📊 Statusleiste verbergen" if self.config.get("show_tamagotchi_hud", True) else "📊 Statusleiste einblenden"
        menu.addAction(hud_text).triggered.connect(self._toggle_hud)

        roam_text = "🚶 Wandern stoppen" if self.config.get("roaming_enabled", True) else "🚶 Selbstständig wandern"
        menu.addAction(roam_text).triggered.connect(self._toggle_roaming)

        # 8. Skalierung Submenü
        scale_menu = menu.addMenu("📏 Größe ändern")
        for s_val, s_name in [(0.50, "Klein (50%)"), (0.70, "Standard (70%)"), (0.85, "Groß (85%)"), (1.0, "Voll (100%)")]:
            act_s = scale_menu.addAction(f"{'✓ ' if abs(self.scale - s_val) < 0.05 else ''}{s_name}")
            act_s.triggered.connect(lambda ch, sv=s_val: self._set_scale(sv))

        menu.addSeparator()

        # 9. Einstellungen
        act_settings = menu.addAction("⚙️ Einstellungen & Dashboard...")
        act_settings.triggered.connect(self._open_settings)

        menu.addSeparator()

        # 10. Beenden
        act_exit = menu.addAction("❌ Beenden")
        act_exit.triggered.connect(self._exit_app)

        menu.exec(event.globalPos())

    def _feed_snack_action(self, snack_type: str):
        msg, icon = self.tamagotchi.feed_snack(snack_type)
        self.speech_bubble_text = msg
        self.speech_bubble_timeout = time.time() + 3.5
        self.current_anim = "waving"
        self.anim_start_time = time.time()
        self.add_particle(icon, QColor(250, 204, 21))
        self.voice.speak(msg)

    def _take_break_action(self):
        self.tamagotchi.take_break()
        self.add_particle("🧘", QColor(34, 197, 94))
        self.add_particle("✨", QColor(250, 204, 21), offset_y=-10)

    def _throw_ball_action(self):
        start_x = self.width() // 2
        start_y = self.height() - 40
        target_x = random.choice([30, self.width() - 30])
        self.ball_game.throw(start_x, start_y, target_x)
        self.speech_bubble_text = "Hui! Wo fliegt der Ball hin?! Ich krieg ihn! 🎾"
        self.speech_bubble_timeout = time.time() + 3.0
        self.sfx.play("ball_catch")

    def _toggle_sleep_action(self):
        is_sleeping = self.tamagotchi.toggle_sleep()
        if is_sleeping:
            self.speech_bubble_text = "Gute Nacht... Zzz..."
            self.speech_bubble_timeout = time.time() + 2.5
            self.current_anim = "idle"
        self.update()

    def _change_voice_quick(self, voice_key: str):
        self.config.set("voice", voice_key)
        vname = VOICES.get(voice_key, {}).get("name", voice_key)
        msg = f"Stimme gewechselt zu {vname}!"
        self.speech_bubble_text = msg
        self.speech_bubble_timeout = time.time() + 3.0
        self.voice.speak("Stimme aktiviert. Ich bin bereit!")

    def _set_theme(self, theme_key: str):
        self.config.set("hud_theme", theme_key)
        self.update()

    def _toggle_hud(self):
        cur = self.config.get("show_tamagotchi_hud", True)
        self.config.set("show_tamagotchi_hud", not cur)
        self.update()

    def _toggle_roaming(self):
        cur = self.config.get("roaming_enabled", True)
        self.config.set("roaming_enabled", not cur)
        if cur:
            self.roam_direction = "idle"
            self.current_anim = "idle"

    def _set_scale(self, s: float):
        self.scale = s
        self.config.set("scale", s)
        self._update_window_size()
        self.update()

    def _open_settings(self):
        dlg = SettingsDialog(self.config, self.voice, self.llm, self.tamagotchi, self)
        if dlg.exec():
            self.scale = float(self.config.get("scale", 0.70))
            self._update_window_size()
            self.update()

    def _exit_app(self):
        self.config.set("pos_x", self.x())
        self.config.set("pos_y", self.y())
        self.voice.stop()
        QApplication.quit()


def print_cli_status(config: ConfigManager):
    v = config.get("vitals", {})
    prog = config.get("progression", {})
    lvl, title, xp = config.get_level_info()

    def bar(val, length=12):
        filled = max(0, min(length, int((val / 100.0) * length)))
        return "█" * filled + "░" * (length - filled)

    h = int(v.get("hunger", 0))
    t = int(v.get("thirst", 0))
    e = int(v.get("energy", 0))

    print("\033[1;36m🐾 Yuyu Desktop Pet & Tamagotchi — Status\033[0m")
    print("\033[1;30m──────────────────────────────────────────────\033[0m")
    print(f"⭐ \033[1;33mLevel {lvl} ({title})\033[0m | {xp} / 1000 XP")
    print(f"🥪 Hunger:  [{bar(h)}] \033[1;32m{h}%\033[0m")
    print(f"💧 Durst:   [{bar(t)}] \033[1;34m{t}%\033[0m")
    print(f"⚡ Energie: [{bar(e)}] \033[1;33m{e}%\033[0m")
    print("\033[1;30m──────────────────────────────────────────────\033[0m")
    print(f"🥤 Wasser heute: {prog.get('water_drank_today', 0)} | 🧘 Pausen: {prog.get('breaks_taken_today', 0)} | 🔥 Streak: {prog.get('streak_days', 1)} Tag(e)")
    print("\033[1;30m──────────────────────────────────────────────\033[0m")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="🐾 Desktop Pet & Tamagotchi AI Companion")
    parser.add_argument("--status", action="store_true", help="Zeigt aktuellen Tamagotchi-Status im Terminal")
    parser.add_argument("--feed", nargs="?", const="sandwich", choices=["sandwich", "apple", "coffee", "water", "donut"], help="Füttert das Pet mit einem Snack")
    parser.add_argument("--drink", action="store_true", help="Gibt dem Pet ein Glas Wasser (+50%% Hydration)")
    parser.add_argument("--break", dest="take_break", action="store_true", help="Markiert eine Bildschirmpause als erledigt")
    parser.add_argument("--say", type=str, help="Lässt das Pet eine Sprachnachricht vorlesen")
    args, unknown = parser.parse_known_args()

    config = ConfigManager()

    if args.status:
        print_cli_status(config)
        return

    if args.feed:
        sfx = RetroSoundSynthesizer()
        voice = VoiceEngine(config, sfx)
        llm = LLMEngine(config)
        tamagotchi = TamagotchiEngine(config, llm, voice, sfx)
        msg, icon = tamagotchi.feed_snack(args.feed)
        print(f"✓ {icon} {msg}")
        return

    if args.drink:
        sfx = RetroSoundSynthesizer()
        voice = VoiceEngine(config, sfx)
        llm = LLMEngine(config)
        tamagotchi = TamagotchiEngine(config, llm, voice, sfx)
        msg, icon = tamagotchi.feed_snack("water")
        print(f"✓ {icon} {msg}")
        return

    if args.take_break:
        sfx = RetroSoundSynthesizer()
        voice = VoiceEngine(config, sfx)
        llm = LLMEngine(config)
        tamagotchi = TamagotchiEngine(config, llm, voice, sfx)
        tamagotchi.take_break()
        print("✓ 🧘 Bildschirmpause eingetragen!")
        return

    if args.say:
        sfx = RetroSoundSynthesizer()
        voice = VoiceEngine(config, sfx)
        print(f"🗣️ Spreche: „{args.say}“...")
        voice.speak(args.say)
        time.sleep(max(2.5, len(args.say) * 0.08))
        return

    app = QApplication(sys.argv)
    app.setApplicationName("DesktopPetCompanion")
    app.setQuitOnLastWindowClosed(False)

    sfx = RetroSoundSynthesizer()
    voice = VoiceEngine(config, sfx)
    llm = LLMEngine(config)
    tamagotchi = TamagotchiEngine(config, llm, voice, sfx)

    window = DesktopPetWindow(config, voice, llm, tamagotchi, sfx)
    window.show()

    sfx.play("happy")
    QTimer.singleShot(1000, lambda: voice.speak("Hallo! Yuyu ist online und behält deinen Tag im Blick! 🐾"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
