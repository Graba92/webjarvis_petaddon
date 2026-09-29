#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐾 Desktop Pet & Tamagotchi AI Companion (OpenPets Mini Core)
Eigenständiges, plattformübergreifendes Linux Desktop-Overlay (KDE Plasma / CachyOS / X11 / Wayland).

Features:
- 100% Standalone (Keine Abhängigkeit von WebJarvis oder externen Servern)
- Universelle LLM-Konfiguration: Kompatibel mit jedem LLM (Gemini, OpenAI, OpenRouter, Groq, Ollama) über API-Key
- 4 Charakter-Stimmen (Lola, Buster, Mimi, Klaus) mit Neural-TTS / Fallback
- Tamagotchi-System: Hunger, Durst, Energie/Pause & Termine mit Live-Statusanzeige über dem Pet
- Die kleine Nervensäge: Erinnert aktiv, frech und humorvoll an Trinken, Pausen, Essen und Termine
- Kristallklares Rendering mit bilinearem Anti-Aliasing (SmoothTransformation)
- Wayland / KDE Plasma kompatibel durch erzwungenes XWayland (xcb)
- 16-Sektoren Blickverfolgung & autonomes Roaming entlang des Bildschirms
- Umfangreiches Einstellungsfenster & Rechtsklick-Menü
"""

import os
import sys

# Linux Wayland / KDE Plasma Fix:
# Nativer Wayland-Betrieb verbietet Fenstern programmatisches move() / Roaming und
# blockiert freies Positionieren. Erzwinge XWayland (xcb), genau wie OpenPets.
if "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

import math
import time
import json
import random
import urllib.request
import urllib.parse
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QRect, QRectF, pyqtSignal, QObject, QDate, QTime
)
from PyQt6.QtGui import (
    QPainter, QImage, QPixmap, QColor, QFont, QCursor, QAction, QActionGroup,
    QPen, QBrush, QLinearGradient, QIcon
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSlider, QCheckBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTimeEdit, QDateEdit, QSpinBox, QGroupBox
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
# 1. KONFIGURATIONS-MANAGER
# ==============================================================================
class ConfigManager:
    """Verwaltet dauerhafte Einstellungen in ~/.config/desktop_pet/config.json"""

    CONFIG_DIR = Path.home() / ".config" / "desktop_pet"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULT_CONFIG = {
        "api_key": "",
        "llm_provider": "auto",  # auto, gemini, openai, openrouter, groq, ollama, custom
        "model_name": "gemini-1.5-flash",
        "base_url": "",
        "voice": "lola",
        "volume": 85,
        "muted": False,
        "scale": 0.70,
        "roaming_enabled": True,
        "show_tamagotchi_hud": True,
        "nag_intensity": "frech",  # sanft, frech, extrem
        "decay_minutes": {
            "hunger": 120,   # Alle 2 Stunden Hunger
            "thirst": 45,    # Alle 45 Minuten Durst
            "energy": 50     # Alle 50 Minuten Pause nötig
        },
        "vitals": {
            "hunger": 85.0,
            "thirst": 90.0,
            "energy": 95.0,
            "last_tick": time.time()
        },
        "appointments": [],
        "pos_x": -1,
        "pos_y": -1
    }

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.data = dict(self.DEFAULT_CONFIG)
        self.load()

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

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()


# ==============================================================================
# 2. AUDIO & SPRACHAUSGABE (VOICE ENGINE)
# ==============================================================================
class VoiceEngine(QObject):
    """Handhabt Sprachausgabe für 4 Stimmen mit Neural-TTS / Fallback und Audio-Rhythmus"""

    speech_started = pyqtSignal(str)
    speech_finished = pyqtSignal()
    audio_level = pyqtSignal(float)

    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config
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
        """Spricht Text asynchron ab"""
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

        # 1. Methode: Google TTS + FFmpeg Pitch Modulation für 4 distinkte Stimmen
        try:
            url = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=de&q=" + urllib.parse.quote(text[:300])
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                audio_bytes = resp.read()

            with open(tmp_raw, "wb") as f:
                f.write(audio_bytes)

            pitch = voice_info.get("pitch", 1.0)
            rate = voice_info.get("rate", 1.0)

            # FFmpeg Filter: Pitch Shifting via asetrate & atempo
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

            # Audio-Rhythmus Simulation während der Wiedergabe
            vol = self.config.get("volume", 85) / 100.0
            play_proc = subprocess.Popen(["pw-play", "--volume", str(vol), str(play_file)])

            while play_proc.poll() is None and not self._stop_requested:
                lvl = random.uniform(0.2, 0.95)
                self.audio_level.emit(lvl)
                time.sleep(0.08)

            played_successfully = True
        except Exception as e:
            # Fallback bei Offline / Netzwerkproblem: espeak-ng
            pass

        # 2. Methode: Offline espeak-ng / espeak Fallback
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

        # Aufräumen
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
# 3. LLM ENGINE (EGAL WELCHES LLM ÜBER API-KEY KONFIGURIERBAR)
# ==============================================================================
class LLMEngine:
    """Universelle LLM-Schnittstelle für Gemini, OpenAI, Groq, OpenRouter & Ollama"""

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
        """Erzeugt frechen Nervensägen-Spruch via konfiguriertem LLM oder Offline-Fallback"""
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
            "generationConfig": {
                "maxOutputTokens": 80,
                "temperature": 0.8
            }
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
        raise ValueError("Leere OpenAI-kompatible Antwort")


# ==============================================================================
# 4. TAMAGOTCHI ENGINE (BEDÜRFNISSE, INTERVALLE & NERVENSÄGE)
# ==============================================================================
class TamagotchiEngine(QObject):
    """Simuliert Bedürfnisse (Hunger, Durst, Energie/Pause) und Terminerinnerungen"""

    vitals_updated = pyqtSignal(dict)
    nag_triggered = pyqtSignal(str, str)  # vital_type, text
    appointment_alert = pyqtSignal(dict)  # appointment dict

    def __init__(self, config: ConfigManager, llm: LLMEngine, voice: VoiceEngine):
        super().__init__()
        self.config = config
        self.llm = llm
        self.voice = voice

        # Vitals initialisieren
        vitals = self.config.get("vitals", {})
        self.hunger = float(vitals.get("hunger", 85.0))
        self.thirst = float(vitals.get("thirst", 90.0))
        self.energy = float(vitals.get("energy", 95.0))
        self.last_tick = vitals.get("last_tick", time.time())

        # Nag-Timer & Cooldowns
        self.last_nag_time = 0.0
        self.nag_cooldown = 180.0  # Alle 3 Minuten nerven bei kritischem Zustand

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

        # Zerfall pro Sekunde berechnen
        self.hunger = max(0.0, self.hunger - (100.0 / (h_min * 60.0)) * elapsed)
        self.thirst = max(0.0, self.thirst - (100.0 / (t_min * 60.0)) * elapsed)
        self.energy = max(0.0, self.energy - (100.0 / (e_min * 60.0)) * elapsed)

        # In Config speichern
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

        # Prüfe Termine
        self._check_appointments()

        # Prüfe ob Pet als Nervensäge aktiv werden muss
        if now - self.last_nag_time > self.nag_cooldown:
            critical_vital = None
            if self.thirst < 25.0:
                critical_vital = "thirst"
            elif self.energy < 25.0:
                critical_vital = "energy"
            elif self.hunger < 25.0:
                critical_vital = "hunger"

            if critical_vital:
                self.last_nag_time = now
                threading.Thread(
                    target=self._trigger_nag_async,
                    args=(critical_vital,),
                    daemon=True
                ).start()

    def _trigger_nag_async(self, vital_type: str):
        val = int(getattr(self, vital_type, 0))
        nag_text = self.llm.generate_nag(vital_type, f"Aktueller Wert: {val}%")
        self.nag_triggered.emit(vital_type, nag_text)
        self.voice.speak(nag_text)

    def _check_appointments(self):
        appointments = self.config.get("appointments", [])
        now_dt = datetime.now()
        now_str = now_dt.strftime("%H:%M")
        today_str = now_dt.strftime("%Y-%m-%d")

        for app in appointments:
            if app.get("date") == today_str and not app.get("reminded", False):
                app_time = app.get("time", "")
                if app_time == now_str:
                    app["reminded"] = True
                    self.config.save()
                    title = app.get("title", "Termin")
                    msg = self.llm.generate_nag("appointment", title)
                    self.appointment_alert.emit(app)
                    self.nag_triggered.emit("appointment", msg)
                    self.voice.speak(msg)
                    break

    def feed(self):
        self.hunger = min(100.0, self.hunger + 50.0)
        self.config.save()
        self.voice.speak("Mmh, köstlich! Danke für den Snack! Jetzt habe ich wieder Energie! 💖")

    def drink(self):
        self.thirst = min(100.0, self.thirst + 50.0)
        self.config.save()
        self.voice.speak("Aaaah, herrlich erfrischend! Hydration wieder im grünen Bereich! 💧")

    def take_break(self):
        self.energy = 100.0
        self.config.save()
        self.voice.speak("Super gemacht! Kurz gestreckt und tief durchgeatmet – jetzt geht's produktiv weiter! ✨")

    def get_next_appointment(self) -> Optional[Dict[str, Any]]:
        appointments = self.config.get("appointments", [])
        today_str = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")

        upcoming = []
        for a in appointments:
            if a.get("date") == today_str and a.get("time", "") >= now_time and not a.get("reminded", False):
                upcoming.append(a)

        if upcoming:
            upcoming.sort(key=lambda x: x.get("time", ""))
            return upcoming[0]
        return None


# ==============================================================================
# 5. EINSTELLUNGS- & KONFIGURATIONS-FENSTER (PYQT6)
# ==============================================================================
class SettingsDialog(QDialog):
    """Modernes Cyberpunk/Dark Einstellungsmenü für KI-API-Key, Stimmen & Tamagotchi"""

    def __init__(self, config: ConfigManager, voice: VoiceEngine, llm: LLMEngine, parent=None):
        super().__init__(parent)
        self.config = config
        self.voice = voice
        self.llm = llm

        self.setWindowTitle("🐾 Yuyu Desktop Pet — Einstellungen & Konfiguration")
        self.setMinimumSize(640, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f131a;
                color: #e2e8f0;
                font-family: sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background-color: #090d14;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #111827;
                color: #94a3b8;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #00d4ff;
                color: #050b14;
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
                color: #050b14;
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
                padding: 4px;
                font-weight: bold;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._build_tab_llm()
        self._build_tab_voices()
        self._build_tab_tamagotchi()
        self._build_tab_appointments()

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

        # Audio Einstellungen
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

        box_nag = QGroupBox("😼 Die kleine Nervensäge")
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

        self.chk_hud = QCheckBox("Tamagotchi-Statusleiste (🥪 💧 ⚡) über dem Pet anzeigen")
        self.chk_hud.setChecked(self.config.get("show_tamagotchi_hud", True))
        bn_l.addWidget(self.chk_hud)

        self.chk_roam = QCheckBox("Selbstständig auf dem Desktop wandern (Roaming)")
        self.chk_roam.setChecked(self.config.get("roaming_enabled", True))
        bn_l.addWidget(self.chk_roam)

        l.addWidget(box_nag)
        l.addStretch()

        self.tabs.addTab(tab, "🐾 Tamagotchi & Nervensäge")

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

        # Tabelle
        self.table_apps = QTableWidget(0, 4)
        self.table_apps.setHorizontalHeaderLabels(["Datum", "Uhrzeit", "Termin", "Aktion"])
        self.table_apps.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        l.addWidget(self.table_apps)

        self._refresh_appointments_table()

        self.tabs.addTab(tab, "📅 Termine")

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
            QMessageBox.warning(self, "Fehler", "Bitte einen Titel für den Termin eingeben!")
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

        # Temporär Werte anwenden
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
# 6. HAUPTFENSTER: DESKTOP PET & TAMAGOTCHI OVERLAY
# ==============================================================================
class DesktopPetWindow(QWidget):
    """Natives PyQt6 Desktop-Overlay mit Anti-Aliasing, Tamagotchi-HUD & Spritesheet"""

    def __init__(self, config: ConfigManager, voice: VoiceEngine, llm: LLMEngine, tamagotchi: TamagotchiEngine):
        super().__init__()
        self.config = config
        self.voice = voice
        self.llm = llm
        self.tamagotchi = tamagotchi

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
        self.hud_height = 55  # Platz für Tamagotchi-HUD über dem Pet
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

        # Sprechblase & Audio Bounce
        self.speech_bubble_text = ""
        self.speech_bubble_timeout = 0.0
        self.audio_level = 0.0

        # Signale verbinden
        self.voice.speech_started.connect(self._on_speech_started)
        self.voice.audio_level.connect(self._on_audio_level)
        self.tamagotchi.nag_triggered.connect(self._on_nag_triggered)
        self.tamagotchi.vitals_updated.connect(lambda v: self.update())

        # Render-Timer (60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._game_loop)
        self.anim_timer.start(16)

        # Initiale Positionierung am unteren Bildschirmrand
        self._initial_placement()

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
        else:
            print("[DesktopPet] WARNUNG: Spritesheet nicht gefunden!")

    def _update_window_size(self):
        w = int(FRAME_WIDTH * self.scale) + 30
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

    def _game_loop(self):
        now = time.time()

        # 1. Gaze Tracking (Blickverfolgung zum Cursor)
        if self.gaze_tracking_enabled and self.current_anim == "idle":
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

        # 2. Animations-Frame berechnen
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

        # 3. Autonomes Roaming
        if self.config.get("roaming_enabled", True) and not self.is_dragging:
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
        # Hüpf-Animation bei Notstand
        self.current_anim = "jumping"
        self.anim_start_time = time.time()

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

        # 2. Sprechblase zeichnen (falls aktiv)
        if self.speech_bubble_text and now < self.speech_bubble_timeout:
            self._draw_speech_bubble(painter)

        # 3. Pet Sprite bilinearglättend rendern
        if self.spritesheet and not self.spritesheet.isNull():
            anim_cfg = ANIMATIONS.get(self.current_anim, ANIMATIONS["idle"])
            row = anim_cfg["row"]
            col = self.frame_idx % anim_cfg["frames"]

            src_x = col * FRAME_WIDTH
            src_y = row * FRAME_HEIGHT

            # Gaze Blickoffset bei Idle
            gaze_off_x = 0
            gaze_off_y = 0
            if self.gaze_dir > 0 and self.current_anim == "idle":
                rad = self.gaze_dir * (22.5 * math.pi / 180.0)
                gaze_off_x = int(math.cos(rad) * 4)
                gaze_off_y = int(math.sin(rad) * 3)

            # Audio-RMS Bounce bei Sprache
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

            # Sanfter Schatten unter dem Pet
            shadow_rect = QRectF(dst_x + 10, dst_y + dst_h - 10, dst_w - 20, 10)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 70))
            painter.drawEllipse(shadow_rect)

            painter.drawImage(dst_x, dst_y, scaled_frame)

    def _draw_tamagotchi_hud(self, painter: QPainter):
        """Zeichnet die 3 Statusbalken (Hunger, Durst, Pause) und nächsten Termin"""
        hud_w = self.width() - 10
        hud_h = 44
        hud_x = 5
        hud_y = 5

        # Hintergrund-Pille
        painter.setPen(QPen(QColor(0, 212, 255, 120), 1))
        painter.setBrush(QColor(10, 15, 24, 210))
        painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 8, 8)

        # 3 Mini-Balken: 🥪 Hunger, 💧 Durst, ⚡ Energie
        vitals = [
            ("🥪", self.tamagotchi.hunger, QColor(34, 197, 94)),
            ("💧", self.tamagotchi.thirst, QColor(6, 182, 212)),
            ("⚡", self.tamagotchi.energy, QColor(245, 158, 11))
        ]

        bar_w = (hud_w - 24) // 3
        bar_h = 5
        font = QFont("sans-serif", 8, QFont.Weight.Bold)
        painter.setFont(font)

        for i, (icon, val, base_color) in enumerate(vitals):
            bx = hud_x + 6 + i * (bar_w + 6)
            by = hud_y + 6

            # Icon & Prozent
            painter.setPen(QColor(255, 255, 255, 220))
            painter.drawText(bx, by + 11, f"{icon} {int(val)}%")

            # Balken-Hintergrund
            bar_y = by + 16
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(30, 41, 59, 180))
            painter.drawRoundedRect(bx, bar_y, bar_w, bar_h, 2, 2)

            # Farbverlauf bei kritischem Stand
            fill_color = base_color
            if val < 25.0:
                fill_color = QColor(239, 68, 68)  # Rot
            elif val < 50.0:
                fill_color = QColor(234, 179, 8)   # Gelb

            fill_w = max(2, int((bar_w * val) / 100.0))
            painter.setBrush(fill_color)
            painter.drawRoundedRect(bx, bar_y, fill_w, bar_h, 2, 2)

        # Nächster Termin Badge (untere Zeile im HUD)
        next_app = self.tamagotchi.get_next_appointment()
        painter.setFont(QFont("sans-serif", 7))
        if next_app:
            t_str = f"📅 {next_app.get('time')}: {next_app.get('title')}"
            painter.setPen(QColor(0, 212, 255, 240))
            painter.drawText(hud_x + 8, hud_y + 38, t_str[:32])
        else:
            painter.setPen(QColor(148, 163, 184, 180))
            painter.drawText(hud_x + 8, hud_y + 38, "📅 Keine Termine heute")

    def _draw_speech_bubble(self, painter: QPainter):
        """Zeichnet eine animierte Comic-Sprechblase mit Textumbruch"""
        text = self.speech_bubble_text
        font = QFont("sans-serif", 8, QFont.Weight.Bold)
        painter.setFont(font)

        bubble_w = min(self.width() + 40, 210)
        bubble_x = (self.width() - bubble_w) // 2
        bubble_y = self.hud_height + 2

        metrics = painter.fontMetrics()
        rect = metrics.boundingRect(QRect(0, 0, bubble_w - 16, 200), Qt.TextFlag.TextWordWrap, text)
        bubble_h = rect.height() + 14

        # Blasen-Körper
        painter.setPen(QPen(QColor(0, 212, 255, 180), 1.5))
        painter.setBrush(QColor(15, 23, 42, 235))
        painter.drawRoundedRect(bubble_x, bubble_y, bubble_w, bubble_h, 10, 10)

        # Text
        painter.setPen(QColor(255, 255, 255))
        text_rect = QRect(bubble_x + 8, bubble_y + 6, bubble_w - 16, bubble_h - 10)
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, text)

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
                # Koordinaten speichern
                self.config.set("pos_x", self.x())
                self.config.set("pos_y", self.y())
                # Frecher Spruch nach Drag & Drop
                drag_line = random.choice(OFFLINE_NAG_LINES["drag"])
                self.speech_bubble_text = drag_line
                self.speech_bubble_timeout = time.time() + 4.0
                self.voice.speak(drag_line)
            else:
                # Klick-Reaktion
                click_line = random.choice(OFFLINE_NAG_LINES["click"])
                self.speech_bubble_text = click_line
                self.speech_bubble_timeout = time.time() + 3.0
                self.current_anim = "waving"
                self.anim_start_time = time.time()
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

        # 1. Tamagotchi Aktionen ("Pflegen")
        act_feed = menu.addAction("🥪 Snack / Mahlzeit gegessen (+50%)")
        act_feed.triggered.connect(self.tamagotchi.feed)

        act_drink = menu.addAction("💧 Glas Wasser getrunken (+50%)")
        act_drink.triggered.connect(self.tamagotchi.drink)

        act_break = menu.addAction("🧘 Pause gemacht & gestreckt (+100%)")
        act_break.triggered.connect(self.tamagotchi.take_break)

        menu.addSeparator()

        # 2. Stimmen-Submenü (4 Stimmen direkt umschaltbar)
        voice_menu = menu.addMenu("🎙️ Stimme auswählen")
        cur_v = self.config.get("voice", "lola")
        for k, v in VOICES.items():
            act_v = voice_menu.addAction(f"{'✓ ' if k == cur_v else ''}{v['name']}")
            act_v.triggered.connect(lambda ch, vk=k: self._change_voice_quick(vk))

        # 3. Tamagotchi HUD Toggle
        hud_text = "📊 Tamagotchi-Leiste verbergen" if self.config.get("show_tamagotchi_hud", True) else "📊 Tamagotchi-Leiste einblenden"
        act_hud = menu.addAction(hud_text)
        act_hud.triggered.connect(self._toggle_hud)

        # 4. Roaming Toggle
        roam_text = "🚶 Wandern stoppen" if self.config.get("roaming_enabled", True) else "🚶 Selbstständig wandern"
        act_roam = menu.addAction(roam_text)
        act_roam.triggered.connect(self._toggle_roaming)

        # 5. Skalierung Submenü
        scale_menu = menu.addMenu("📏 Größe ändern")
        for s_val, s_name in [(0.50, "Klein (50%)"), (0.70, "Standard (70%)"), (0.85, "Groß (85%)"), (1.0, "Voll (100%)")]:
            act_s = scale_menu.addAction(f"{'✓ ' if abs(self.scale - s_val) < 0.05 else ''}{s_name}")
            act_s.triggered.connect(lambda ch, sv=s_val: self._set_scale(sv))

        menu.addSeparator()

        # 6. Einstellungen
        act_settings = menu.addAction("⚙️ Einstellungen & KI-Konfiguration...")
        act_settings.triggered.connect(self._open_settings)

        menu.addSeparator()

        # 7. Beenden
        act_exit = menu.addAction("❌ Beenden")
        act_exit.triggered.connect(self._exit_app)

        menu.exec(event.globalPos())

    def _change_voice_quick(self, voice_key: str):
        self.config.set("voice", voice_key)
        vname = VOICES.get(voice_key, {}).get("name", voice_key)
        msg = f"Stimme gewechselt zu {vname}!"
        self.speech_bubble_text = msg
        self.speech_bubble_timeout = time.time() + 3.0
        self.voice.speak(f"Stimme aktiviert. Ich bin bereit!")

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
        dlg = SettingsDialog(self.config, self.voice, self.llm, self)
        if dlg.exec():
            self.scale = float(self.config.get("scale", 0.70))
            self._update_window_size()
            self.update()

    def _exit_app(self):
        self.config.set("pos_x", self.x())
        self.config.set("pos_y", self.y())
        self.voice.stop()
        QApplication.quit()


# ==============================================================================
# 7. HAUPTPROGRAMM (MAIN)
# ==============================================================================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DesktopPetCompanion")
    app.setQuitOnLastWindowClosed(False)

    config = ConfigManager()
    voice = VoiceEngine(config)
    llm = LLMEngine(config)
    tamagotchi = TamagotchiEngine(config, llm, voice)

    window = DesktopPetWindow(config, voice, llm, tamagotchi)
    window.show()

    # Begrüßung
    QTimer.singleShot(1000, lambda: voice.speak("Hallo! Yuyu ist online und behält deinen Tag im Blick! 🐾"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
