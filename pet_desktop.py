#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐾 WebJarvis Desktop Pet — Yuyu Chibi Companion (OpenPets Mini Core)
Natives, transparentes Linux Desktop-Overlay (KDE Plasma / CachyOS) mit PyQt6.

Verbesserungen:
- Kristallklares Rendering mit bilinearem Anti-Aliasing (SmoothTransformation, keine Pixel-Artefakte!)
- Bulletproof Drag & Drop: Zuverlässiges Bewegen mit Maus, WebJarvis bemerkt Verschiebung
- Live Stimmenwechsel ohne Neustart (Männlich: Puck / Weiblich: Aoede)
- Umfangreiches Rechtsklick-Menü:
  * 🎙️ Stimme wechseln
  * ⚡ Jarvis Session / Mikrofon Stummschalten / Entstummen
  * ⏹️ Sprachausgabe unterbrechen (Interrupt)
  * 🌐 WebJarvis Webinterface im Browser öffnen
  * 📏 Skalierung (40%, 55%, 75%, 100%, 125%)
  * 🚶 Wandern an/aus, 👁️ Gaze an/aus, 💬 Sprechblasen an/aus, 💖 Streicheln
  * ❌ Beenden
- Audio-Rhythmus: Bounced sanft bei aktiver Sprachausgabe (audio_level)
"""

import os
import sys

# OpenPets Linux Wayland / KDE Plasma Fix:
# Nativer Wayland-Betrieb verbietet Top-Level-Fenstern programmatisches move() / Roaming und
# blockiert freies Positionieren. Wie bei OpenPets forciert das Pet XWayland (xcb),
# damit Roaming und Drag & Drop uneingeschränkt auf allen Displays funktionieren.
if "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

import math
import time
import json
import random
import threading
import asyncio
import webbrowser
from pathlib import Path

from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QRect, QRectF, pyqtSignal, QObject
)
from PyQt6.QtGui import (
    QPainter, QImage, QPixmap, QColor, QFont, QCursor, QAction, QActionGroup, QPen, QBrush
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu
)

try:
    import websockets
except ImportError:
    websockets = None

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

RANDOM_DIALOGUES = [
    "Ich passe auf dein System auf! ✨",
    "CachyOS läuft geschmeidig wie Butter!",
    "Alles nominal, Operator!",
    "Brauchst du Hilfe bei einem Task? 💖",
    "PipeWire Audio & Neural-Cores aktiv!",
    "Yuyu ist stets einsatzbereit!",
    "J.A.R.V.I.S. und ich sind ein unschlagbares Team.",
]

RANDOM_MOVE_RESPONSES = [
    "Huiii! Neuer Aussichtspunkt! 🚀",
    "Hier gefällt es mir super!",
    "Rundflug über deinen Desktop beendet! ✨",
    "Von hier oben behalte ich alles im Blick!",
    "Sanfte Landung geglückt! 🐾",
]


class WebSocketBridgeSignals(QObject):
    jarvis_state_changed = pyqtSignal(str)
    jarvis_speech_received = pyqtSignal(str)
    voice_updated = pyqtSignal(str)
    audio_level_received = pyqtSignal(float)
    mute_state_changed = pyqtSignal(bool)


class JarvisWebSocketClient(threading.Thread):
    def __init__(self, signals: WebSocketBridgeSignals, url: str = "ws://127.0.0.1:8765"):
        super().__init__(daemon=True)
        self.signals = signals
        self.url = url
        self.loop = None
        self.ws = None
        self.running = True

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_loop())

    async def _connect_loop(self):
        while self.running:
            try:
                if websockets:
                    async with websockets.connect(self.url) as ws:
                        self.ws = ws
                        await ws.send(json.dumps({"type": "get_voice"}))
                        async for message in ws:
                            try:
                                data = json.loads(message)
                                msg_type = data.get("type", "")

                                if msg_type == "state":
                                    self.signals.jarvis_state_changed.emit(data.get("state", "IDLE"))

                                elif msg_type == "chat":
                                    spk = data.get("speaker", "")
                                    txt = data.get("text", "")
                                    if spk == "JARVIS" and txt:
                                        self.signals.jarvis_speech_received.emit(txt)

                                elif msg_type in ("voice_updated", "voice_status"):
                                    self.signals.voice_updated.emit(data.get("voice", "Puck"))

                                elif msg_type == "audio_level":
                                    lvl = float(data.get("level", 0.0))
                                    self.signals.audio_level_received.emit(lvl)

                                elif msg_type == "mute_state":
                                    muted = bool(data.get("muted", False))
                                    self.signals.mute_state_changed.emit(muted)

                                elif msg_type in ("init", "SYSTEM_INIT"):
                                    vc = data.get("voice_name") or data.get("data", {}).get("voice_name")
                                    if vc:
                                        self.signals.voice_updated.emit(vc)
                                    if "is_muted" in data:
                                        self.signals.mute_state_changed.emit(bool(data["is_muted"]))

                            except Exception:
                                pass
            except Exception:
                await asyncio.sleep(2.0)

    def send_json(self, payload: dict):
        if self.loop and self.ws:
            asyncio.run_coroutine_threadsafe(
                self._send_raw(payload),
                self.loop
            )

    async def _send_raw(self, payload: dict):
        try:
            if self.ws:
                await self.ws.send(json.dumps(payload))
        except Exception:
            pass


class DesktopPetWindow(QWidget):
    def __init__(self, spritesheet_path: str):
        super().__init__()
        self.spritesheet_path = spritesheet_path
        self.spritesheet = QImage(spritesheet_path)
        if self.spritesheet.isNull():
            print(f"❌ FEHLER: Spritesheet nicht geladen: {spritesheet_path}")

        # Konfiguration & Einstellungen
        self.scale = 0.75  # 75% Standard für gestochen scharfe Details
        self.roaming_enabled = True
        self.gaze_enabled = True
        self.speech_enabled = True
        self.current_voice = "Puck"
        self.is_jarvis_muted = False
        self.jarvis_state = "IDLE"

        # Animations-Status
        self.current_state = "idle"
        self.anim_start_time = time.time()
        self.one_shot_active = False
        self.one_shot_end_time = 0.0
        self.audio_bounce_offset = 0

        # Gaze Tracking
        self.gaze_row = None
        self.gaze_col = None
        self.last_cursor_pos = QPoint(0, 0)
        self.last_cursor_move_time = time.time()

        # Autonomes Roaming
        self.roam_direction = "idle"
        self.roam_end_time = 0.0
        self.next_roam_decision = time.time() + 1.2

        # Bulletproof Drag & Drop Handling
        self.is_dragging = False
        self.drag_start_cursor = QPoint()
        self.drag_start_window = QPoint()

        # Sprechblase
        self.speech_bubble_text = "Hallo! Ich bin Yuyu! 🐾"
        self.speech_bubble_expire = time.time() + 4.5

        # WebSocket Brücke
        self.ws_signals = WebSocketBridgeSignals()
        self.ws_signals.jarvis_state_changed.connect(self.on_jarvis_state)
        self.ws_signals.jarvis_speech_received.connect(self.on_jarvis_speech)
        self.ws_signals.voice_updated.connect(self.on_voice_updated)
        self.ws_signals.audio_level_received.connect(self.on_audio_level)
        self.ws_signals.mute_state_changed.connect(self.on_mute_state)

        self.ws_client = JarvisWebSocketClient(self.ws_signals)
        self.ws_client.start()

        # Fenster-Eigenschaften: 100% transparent, rahmenlos, immer im Vordergrund
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setMouseTracking(True)

        self.update_geometry()

        # Startposition unten rechts über der Taskleiste
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            start_x = geom.width() - int(FRAME_WIDTH * self.scale) - 100
            start_y = geom.height() - int(FRAME_HEIGHT * self.scale) - 50
            self.move(max(50, start_x), max(50, start_y))

        # 60 FPS Render- und Logik-Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(16)

    def update_geometry(self):
        w = int(FRAME_WIDTH * self.scale)
        # Zusätzliche Höhe für Sprechblase und Bounce-Effekt
        h = int(FRAME_HEIGHT * self.scale) + 90
        self.resize(max(240, w + 40), h)

    def show_speech(self, text: str, duration_sec: float = 4.5):
        if not self.speech_enabled:
            return
        if len(text) > 85:
            text = text[:82] + "..."
        self.speech_bubble_text = text
        self.speech_bubble_expire = time.time() + duration_sec
        self.update()

    def set_one_shot(self, state: str, duration_ms: int = 1000, speech: str = None):
        self.current_state = state
        self.anim_start_time = time.time()
        self.one_shot_active = True
        self.one_shot_end_time = time.time() + (duration_ms / 1000.0)
        if speech:
            self.show_speech(speech)
        self.update()

    def on_jarvis_state(self, state: str):
        self.jarvis_state = state
        if self.one_shot_active:
            return

        if state == "THINKING":
            self.current_state = "review"
            self.anim_start_time = time.time()
            self.show_speech("J.A.R.V.I.S. überlegt angestrengt... 🧠", 3.0)
        elif state == "SPEAKING":
            self.current_state = "waving"
            self.anim_start_time = time.time()
        elif state == "ERROR":
            self.current_state = "failed"
            self.anim_start_time = time.time()
            self.show_speech("Oh nein, ein Systemfehler! ⚠️", 4.0)
        elif state == "LISTENING":
            self.current_state = "waiting"
            self.anim_start_time = time.time()
        else:
            self.current_state = "idle"
            self.anim_start_time = time.time()

    def on_jarvis_speech(self, text: str):
        self.set_one_shot("waving", 1400)
        self.show_speech(f"💬 {text}", 6.0)

    def on_voice_updated(self, voice: str):
        self.current_voice = voice

    def on_audio_level(self, level: float):
        # Audio-Bounce wenn gesprochen wird (0 bis 6 Pixel Hüpfen)
        if self.jarvis_state == "SPEAKING" and level > 12.0:
            self.audio_bounce_offset = min(6, int(level / 8.0))
        else:
            self.audio_bounce_offset = 0

    def on_mute_state(self, muted: bool):
        self.is_jarvis_muted = muted

    # =========================================================================
    # Maus & Drag/Drop Handling (Echtes Verschieben über den Desktop)
    # =========================================================================
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.drag_start_cursor = event.globalPosition().toPoint()
            self.drag_start_window = self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_start_cursor
            if delta.manhattanLength() > 5 or self.is_dragging:
                self.is_dragging = True
                new_pos = self.drag_start_window + delta
                self.move(new_pos)
                event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                # Benutzer hat das Pet bewegt!
                # 1. Informiere WebJarvis via WebSocket
                self.ws_client.send_json({
                    "type": "pet_moved",
                    "x": self.x(),
                    "y": self.y()
                })
                # 2. Zeige eigene fröhliche Reaktion
                self.set_one_shot(
                    "jumping",
                    840,
                    random.choice(RANDOM_MOVE_RESPONSES)
                )
            else:
                # Normaler Klick / Streicheln
                self.set_one_shot(
                    "jumping",
                    840,
                    random.choice(RANDOM_DIALOGUES)
                )
            event.accept()

    # =========================================================================
    # Kontextmenü (Rechtsklick) mit allen Steuerungen
    # =========================================================================
    def show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0b0f17;
                color: #e6edf3;
                border: 1px solid #00d4ff;
                border-radius: 8px;
                padding: 6px;
                font-family: sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 26px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 212, 255, 0.28);
                color: #00d4ff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #21262d;
                margin: 4px 8px;
            }
        """)

        # Kopfzeile
        title_action = menu.addAction(f"🐾 Yuyu Chibi — Jarvis Companion")
        title_action.setEnabled(False)
        menu.addSeparator()

        # 🎙️ Stimmenauswahl (Live ohne Neustart!)
        voice_menu = menu.addMenu("🎙️ Jarvis Stimme (Live TTS)")
        voice_group = QActionGroup(self)

        male_act = QAction("👨 Männlich (Puck / Standard)", self, checkable=True)
        male_act.setChecked(self.current_voice != "Aoede")
        male_act.triggered.connect(lambda: self.switch_voice("Puck"))
        voice_group.addAction(male_act)
        voice_menu.addAction(male_act)

        female_act = QAction("👩 Weiblich (Aoede / Sanft & Natürlich)", self, checkable=True)
        female_act.setChecked(self.current_voice == "Aoede")
        female_act.triggered.connect(lambda: self.switch_voice("Aoede"))
        voice_group.addAction(female_act)
        voice_menu.addAction(female_act)

        # ⚡ Jarvis Schnellaktionen
        control_menu = menu.addMenu("⚡ Jarvis Aktionen")
        
        mic_text = "🎙️ Mikrofon stummschalten" if not self.is_jarvis_muted else "🎤 Mikrofon aktivieren"
        mic_act = control_menu.addAction(mic_text)
        mic_act.triggered.connect(self.toggle_mic)

        stop_speech_act = control_menu.addAction("⏹️ Sprachausgabe stoppen (Interrupt)")
        stop_speech_act.triggered.connect(lambda: self.ws_client.send_json({"type": "interrupt"}))

        web_act = control_menu.addAction("🌐 WebJarvis Interface öffnen")
        web_act.triggered.connect(lambda: webbrowser.open("http://localhost:3000"))

        menu.addSeparator()

        # 📏 Skalierung
        size_menu = menu.addMenu("📏 Pet Größe")
        size_group = QActionGroup(self)
        sizes = [
            ("Mini (40%)", 0.40),
            ("Klein (55%)", 0.55),
            ("Normal (75%)", 0.75),
            ("Groß (100%)", 1.00),
            ("Riesig (125%)", 1.25),
        ]
        for label, val in sizes:
            act = QAction(label, self, checkable=True)
            act.setChecked(abs(self.scale - val) < 0.05)
            act.triggered.connect(lambda _, s=val: self.set_scale(s))
            size_group.addAction(act)
            size_menu.addAction(act)

        # 🚶 Wandern Toggle
        roam_act = QAction("🚶 Autonomes Wandern", self, checkable=True)
        roam_act.setChecked(self.roaming_enabled)
        roam_act.triggered.connect(self.toggle_roaming)
        menu.addAction(roam_act)

        # 👁️ Gaze Toggle
        gaze_act = QAction("👁️ Mauszeiger verfolgen (Gaze)", self, checkable=True)
        gaze_act.setChecked(self.gaze_enabled)
        gaze_act.triggered.connect(self.toggle_gaze)
        menu.addAction(gaze_act)

        # 💬 Sprechblasen Toggle
        speech_act = QAction("💬 Sprechblasen anzeigen", self, checkable=True)
        speech_act.setChecked(self.speech_enabled)
        speech_act.triggered.connect(self.toggle_speech)
        menu.addAction(speech_act)

        # 💖 Pet Interaktion
        pet_act = menu.addAction("💖 Streicheln / Tanzen")
        pet_act.triggered.connect(lambda: self.set_one_shot("jumping", 840, "Schnurr... 💖"))

        menu.addSeparator()

        # ❌ Beenden
        quit_act = menu.addAction("❌ Pet beenden")
        quit_act.triggered.connect(self.close)

        menu.exec(global_pos)

    def switch_voice(self, voice_name: str):
        self.current_voice = voice_name
        self.ws_client.send_json({"type": "set_voice", "voice": voice_name})
        gender = "Weiblich (Aoede)" if voice_name == "Aoede" else "Männlich (Puck)"
        self.show_speech(f"Stimme live gewechselt: {gender} 🎙️", 4.0)

    def toggle_mic(self):
        self.ws_client.send_json({"type": "mute_toggle"})
        self.is_jarvis_muted = not self.is_jarvis_muted
        status = "stummgeschaltet" if self.is_jarvis_muted else "aktiviert"
        self.show_speech(f"Mikrofon {status} 🎤", 3.0)

    def set_scale(self, s: float):
        self.scale = s
        self.update_geometry()
        self.update()

    def toggle_roaming(self):
        self.roaming_enabled = not self.roaming_enabled

    def toggle_gaze(self):
        self.gaze_enabled = not self.gaze_enabled

    def toggle_speech(self):
        self.speech_enabled = not self.speech_enabled

    # =========================================================================
    # Hauptschleife (Animations-Ticker, Roaming & Gaze)
    # =========================================================================
    def update_loop(self):
        now = time.time()

        # One-Shot Animation Beendigung
        if self.one_shot_active and now >= self.one_shot_end_time:
            self.one_shot_active = False
            self.current_state = "idle"
            self.anim_start_time = now

        # 16-Sektor Desktop Cursor Gaze
        cursor_pos = QCursor.pos()
        if cursor_pos != self.last_cursor_pos:
            self.last_cursor_pos = cursor_pos
            self.last_cursor_move_time = now

        self.gaze_row = None
        self.gaze_col = None

        if (
            self.gaze_enabled
            and not self.is_dragging
            and not self.one_shot_active
            and self.current_state == "idle"
            and (now - self.last_cursor_move_time < 3.0)
        ):
            target_w = int(FRAME_WIDTH * self.scale)
            target_h = int(FRAME_HEIGHT * self.scale)
            pet_center_x = self.x() + int(target_w / 2)
            pet_center_y = self.y() + 70 + int(target_h / 2)

            dx = cursor_pos.x() - pet_center_x
            dy = cursor_pos.y() - pet_center_y
            dist = math.hypot(dx, dy)

            if dist > 55:  # Deadzone
                angle = math.atan2(dx, -dy)
                sector_count = 16
                sector_angle = (math.pi * 2) / sector_count
                sector = int(math.floor((angle + sector_angle / 2) / sector_angle))
                norm_sector = (sector + sector_count) % sector_count

                if norm_sector < 8:
                    self.gaze_row = 9
                    self.gaze_col = norm_sector
                else:
                    self.gaze_row = 10
                    self.gaze_col = norm_sector - 8

        # Autonomes Roaming am Bildschirmrand
        if self.roaming_enabled and not self.is_dragging and not self.one_shot_active and self.current_state == "idle":
            if now > self.next_roam_decision:
                r = random.random()
                if r < 0.45:
                    self.roam_direction = "left"
                    self.roam_end_time = now + random.uniform(2.0, 3.8)
                elif r < 0.90:
                    self.roam_direction = "right"
                    self.roam_end_time = now + random.uniform(2.0, 3.8)
                else:
                    self.roam_direction = "idle"
                    self.roam_end_time = now + random.uniform(2.5, 4.5)
                self.next_roam_decision = self.roam_end_time + random.uniform(3.5, 7.0)

            if now < self.roam_end_time and self.roam_direction != "idle":
                screen = self.screen() or QApplication.primaryScreen()
                if screen:
                    geom = screen.availableGeometry()
                    speed = 2
                    cur_x = self.x()
                    min_x = geom.left() + 25
                    max_x = geom.right() - int(FRAME_WIDTH * self.scale) - 25

                    if self.roam_direction == "left":
                        new_x = cur_x - speed
                        if new_x <= min_x:
                            self.roam_direction = "right"
                            new_x = min_x
                    else:
                        new_x = cur_x + speed
                        if new_x >= max_x:
                            self.roam_direction = "left"
                            new_x = max_x

                    self.move(new_x, self.y())

        self.update()

    # =========================================================================
    # High-Definition Painting (Anti-Aliased & Kristallklar)
    # =========================================================================
    def paintEvent(self, event):
        if self.spritesheet.isNull():
            return

        painter = QPainter(self)
        # Kristallklares Filtering aktivieren
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        now = time.time()

        # 1. Sprechblase zeichnen
        if self.speech_enabled and self.speech_bubble_text and now < self.speech_bubble_expire:
            font = QFont("sans-serif", 9, QFont.Weight.Bold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(self.speech_bubble_text) + 26
            bubble_width = min(self.width() - 10, max(130, text_width))
            bubble_height = 36

            bubble_x = max(5, int((self.width() - bubble_width) / 2))
            bubble_y = 12

            # Schatten
            painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(bubble_x + 2, bubble_y + 2, bubble_width, bubble_height), 10, 10)

            # Bubble Körper
            painter.setBrush(QBrush(QColor(11, 15, 23, 230)))
            painter.setPen(QPen(QColor(0, 212, 255, 210), 1.5))
            painter.drawRoundedRect(QRectF(bubble_x, bubble_y, bubble_width, bubble_height), 10, 10)

            # Pfeilspitze
            arrow_x = int(self.width() / 2)
            arrow_y = bubble_y + bubble_height
            arrow_pts = [
                QPoint(arrow_x - 6, arrow_y),
                QPoint(arrow_x + 6, arrow_y),
                QPoint(arrow_x, arrow_y + 6)
            ]
            painter.drawPolygon(arrow_pts)

            # Text
            painter.setPen(QColor(225, 245, 255))
            painter.drawText(
                QRect(bubble_x + 6, bubble_y, bubble_width - 12, bubble_height),
                Qt.AlignmentFlag.AlignCenter,
                self.speech_bubble_text
            )

        # 2. Frame-Berechnung
        state = self.current_state

        if self.roaming_enabled and not self.is_dragging and not self.one_shot_active and now < self.roam_end_time and self.roam_direction != "idle":
            state = "running-left" if self.roam_direction == "left" else "running-right"

        source_row = 0
        source_col = 0

        if self.gaze_row is not None and self.gaze_col is not None:
            source_row = self.gaze_row
            source_col = self.gaze_col
        else:
            anim_def = ANIMATIONS.get(state, ANIMATIONS["idle"])
            elapsed_ms = int((now - self.anim_start_time) * 1000)
            duration_ms = anim_def["duration_ms"]
            frames = anim_def["frames"]

            if anim_def["loop"]:
                frame_idx = (elapsed_ms % duration_ms) // (duration_ms // frames)
            else:
                frame_idx = min(frames - 1, elapsed_ms // (duration_ms // frames))

            source_row = anim_def["row"]
            source_col = min(frames - 1, int(frame_idx))

        sx = source_col * FRAME_WIDTH
        sy = source_row * FRAME_HEIGHT

        target_w = int(FRAME_WIDTH * self.scale)
        target_h = int(FRAME_HEIGHT * self.scale)
        target_x = int((self.width() - target_w) / 2)
        target_y = 65 - self.audio_bounce_offset

        # 3. Ausschneiden und hochqualitativ skalieren (Keine Pixelbildung!)
        frame_crop = self.spritesheet.copy(sx, sy, FRAME_WIDTH, FRAME_HEIGHT)
        scaled_frame = frame_crop.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        painter.drawImage(target_x, target_y, scaled_frame)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WebJarvis Desktop Pet")

    # Spritesheet-Pfade ermitteln
    candidates = [
        Path.home() / ".local" / "share" / "webjarvis_petaddon" / "pets" / "yuyu-chibi" / "spritesheet.webp",
        Path(__file__).resolve().parent / "pets" / "yuyu-chibi" / "spritesheet.webp",
        Path("/home/graba/Schreibtisch/ASGRAD/Valhalla/TOOLS/GRABAS_GITHUB/webjarvis_petaddon/pets/yuyu-chibi/spritesheet.webp"),
        Path("/home/graba/Downloads/driver-and tools/yuyu-chibi/spritesheet.webp")
    ]
    spritesheet_path = next((p for p in candidates if p.exists()), candidates[0])

    pet = DesktopPetWindow(str(spritesheet_path))
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
