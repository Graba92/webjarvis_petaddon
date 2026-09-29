#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐾 WebJarvis Desktop Pet — Yuyu Chibi Companion (OpenPets Mini Core)
Läuft nativ auf dem Linux Desktop (KDE Plasma / CachyOS) als transparentes,
rahmenloses Always-on-Top Fenster mit PyQt6.

Features:
- OpenPets V2 Spritesheet Rendering (8x11 Atlas, 192x208 Framegröße)
- 16-Sektor Desktop Cursor Gaze Tracking (folgt der echten Maus auf dem Desktop)
- Autonomes Wandern (Roaming) am unteren Desktop-Bildschirmrand
- Drag & Drop: Mit der Maus frei auf dem Desktop verschiebbar
- Live WebSocket Bridge zu WebJarvis (ws://127.0.0.1:8765):
  * Reagiert auf THINKING, SPEAKING, ERROR, LISTENING
  * Zeigt Sprechblasen auf dem Desktop bei Jarvis-Antworten
- Rechtsklick-Kontextmenü:
  * 🎙️ Stimmenauswahl: Männlich (Puck) / Weiblich (Aoede)
  * 📏 Skalierung (50%, 75%, 100%, 125%)
  * 🚶 Wandern an/aus, 👁️ Gaze an/aus, 💬 Sprechblasen an/aus
  * ❌ Schließen
"""

import sys
import os
import math
import time
import json
import random
import threading
import asyncio
from pathlib import Path

from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QRect, QRectF, pyqtSignal, QObject
)
from PyQt6.QtGui import (
    QPainter, QImage, QColor, QFont, QCursor, QAction, QActionGroup, QPen, QBrush
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu
)

try:
    import websockets
except ImportError:
    websockets = None

# Basis-Konstanten des OpenPets Codex V2 Spritesheets
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


class WebSocketBridgeSignals(QObject):
    jarvis_state_changed = pyqtSignal(str)
    jarvis_speech_received = pyqtSignal(str)
    voice_updated = pyqtSignal(str)


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
                        # Initialer Request für Voice
                        await ws.send(json.dumps({"type": "get_voice"}))
                        async for message in ws:
                            try:
                                data = json.loads(message)
                                msg_type = data.get("type", "")

                                if msg_type == "state":
                                    st = data.get("state", "IDLE")
                                    self.signals.jarvis_state_changed.emit(st)

                                elif msg_type == "chat":
                                    spk = data.get("speaker", "")
                                    txt = data.get("text", "")
                                    if spk == "JARVIS" and txt:
                                        self.signals.jarvis_speech_received.emit(txt)

                                elif msg_type in ("voice_updated", "voice_status"):
                                    vc = data.get("voice", "Puck")
                                    self.signals.voice_updated.emit(vc)

                                elif msg_type in ("init", "SYSTEM_INIT"):
                                    vc = data.get("voice_name") or data.get("data", {}).get("voice_name")
                                    if vc:
                                        self.signals.voice_updated.emit(vc)

                            except Exception:
                                pass
            except Exception:
                await asyncio.sleep(2.5)

    def send_voice(self, voice_name: str):
        if self.loop and self.ws:
            asyncio.run_coroutine_threadsafe(
                self._send_raw({"type": "set_voice", "voice": voice_name}),
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
            print(f"❌ FEHLER: Spritesheet konnte nicht geladen werden: {spritesheet_path}")

        # Konfiguration
        self.scale = 0.70  # Standard-Skalierung
        self.roaming_enabled = True
        self.gaze_enabled = True
        self.speech_enabled = True
        self.current_voice = "Puck"

        # Animations-Status
        self.current_state = "idle"
        self.anim_start_time = time.time()
        self.one_shot_active = False
        self.one_shot_end_time = 0.0

        # Gaze Tracking
        self.gaze_row = None
        self.gaze_col = None
        self.last_cursor_pos = QPoint(0, 0)
        self.last_cursor_move_time = time.time()

        # Autonomes Roaming
        self.roam_direction = "idle"
        self.roam_end_time = 0.0
        self.next_roam_decision = time.time() + 3.0

        # Drag & Drop
        self.dragging = False
        self.drag_offset = QPoint()

        # Sprechblase
        self.speech_bubble_text = "Hallo! Ich bin Yuyu! 🐾"
        self.speech_bubble_expire = time.time() + 4.5

        # WebSocket Brücke
        self.ws_signals = WebSocketBridgeSignals()
        self.ws_signals.jarvis_state_changed.connect(self.on_jarvis_state)
        self.ws_signals.jarvis_speech_received.connect(self.on_jarvis_speech)
        self.ws_signals.voice_updated.connect(self.on_voice_updated)

        self.ws_client = JarvisWebSocketClient(self.ws_signals)
        self.ws_client.start()

        # Fenster-Flags: Vollständig transparent, kein Rahmen, immer oben
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.update_geometry()

        # Startposition unten rechts über der Taskleiste
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            start_x = geom.width() - int(FRAME_WIDTH * self.scale) - 80
            start_y = geom.height() - int(FRAME_HEIGHT * self.scale) - 40
            self.move(start_x, start_y)

        # 60 FPS Timer für butterweiches Rendern und Logik
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(16)

    def update_geometry(self):
        w = int(FRAME_WIDTH * self.scale)
        # Extra Höhe für die Sprechblase über dem Kopf
        h = int(FRAME_HEIGHT * self.scale) + 80
        self.resize(max(200, w), h)

    def show_speech(self, text: str, duration_sec: float = 4.5):
        if not self.speech_enabled:
            return
        # Text kürzen, falls zu lang
        if len(text) > 80:
            text = text[:77] + "..."
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
        if self.one_shot_active:
            return
        if state == "THINKING":
            self.current_state = "review"
            self.anim_start_time = time.time()
            self.show_speech("J.A.R.V.I.S. überlegt... 🧠", 3.0)
        elif state == "SPEAKING":
            self.current_state = "waving"
            self.anim_start_time = time.time()
        elif state == "ERROR":
            self.current_state = "failed"
            self.anim_start_time = time.time()
            self.show_speech("Ein Fehler ist aufgetreten! ⚠️", 4.0)
        elif state == "LISTENING":
            self.current_state = "waiting"
            self.anim_start_time = time.time()
        else:
            self.current_state = "idle"
            self.anim_start_time = time.time()

    def on_jarvis_speech(self, text: str):
        self.set_one_shot("waving", 1200)
        self.show_speech(f"💬 {text}", 5.5)

    def on_voice_updated(self, voice: str):
        self.current_voice = voice

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging:
                self.dragging = False
                # Wenn nur kurz geklickt wurde: Streichel-Reaktion!
                self.set_one_shot(
                    "jumping",
                    840,
                    random.choice(RANDOM_DIALOGUES)
                )
            event.accept()

    def show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0d1117;
                color: #e6edf3;
                border: 1px solid #00d4ff;
                border-radius: 8px;
                padding: 6px;
                font-family: sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 212, 255, 0.25);
                color: #00d4ff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #30363d;
                margin: 4px 8px;
            }
        """)

        # Titel / Info
        title_action = menu.addAction(f"🐾 Yuyu Chibi Companion")
        title_action.setEnabled(False)
        menu.addSeparator()

        # 🎙️ Stimmenauswahl
        voice_menu = menu.addMenu("🎙️ Jarvis Stimme auswählen")
        voice_group = QActionGroup(self)

        male_act = QAction("👨 Männlich (Puck / Standard)", self, checkable=True)
        male_act.setChecked(self.current_voice != "Aoede")
        male_act.triggered.connect(lambda: self.switch_voice("Puck"))
        voice_group.addAction(male_act)
        voice_menu.addAction(male_act)

        female_act = QAction("👩 Weiblich (Aoede / Sanft)", self, checkable=True)
        female_act.setChecked(self.current_voice == "Aoede")
        female_act.triggered.connect(lambda: self.switch_voice("Aoede"))
        voice_group.addAction(female_act)
        voice_menu.addAction(female_act)

        menu.addSeparator()

        # 📏 Skalierung
        size_menu = menu.addMenu("📏 Pet Größe")
        size_group = QActionGroup(self)
        for label, val in [("Klein (50%)", 0.50), ("Normal (70%)", 0.70), ("Groß (100%)", 1.00), ("Riesig (125%)", 1.25)]:
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
        gaze_act = QAction("👁️ Blickverfolgung (Gaze)", self, checkable=True)
        gaze_act.setChecked(self.gaze_enabled)
        gaze_act.triggered.connect(self.toggle_gaze)
        menu.addAction(gaze_act)

        # 💬 Sprechblasen Toggle
        speech_act = QAction("💬 Sprechblasen", self, checkable=True)
        speech_act.setChecked(self.speech_enabled)
        speech_act.triggered.connect(self.toggle_speech)
        menu.addAction(speech_act)

        menu.addSeparator()

        # ❌ Beenden
        quit_act = menu.addAction("❌ Pet beenden")
        quit_act.triggered.connect(self.close)

        menu.exec(global_pos)

    def switch_voice(self, voice_name: str):
        self.current_voice = voice_name
        self.ws_client.send_voice(voice_name)
        gender = "Weiblich (Aoede)" if voice_name == "Aoede" else "Männlich (Puck)"
        self.show_speech(f"Stimme gewechselt: {gender} 🎙️", 3.5)

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

    def update_loop(self):
        now = time.time()

        # 1. One-Shot Beendigung
        if self.one_shot_active and now >= self.one_shot_end_time:
            self.one_shot_active = False
            self.current_state = "idle"
            self.anim_start_time = now

        # 2. Maus-Cursor Gaze Tracking auf dem gesamten Desktop
        cursor_pos = QCursor.pos()
        if cursor_pos != self.last_cursor_pos:
            self.last_cursor_pos = cursor_pos
            self.last_cursor_move_time = now

        self.gaze_row = None
        self.gaze_col = None

        if (
            self.gaze_enabled
            and not self.dragging
            and not self.one_shot_active
            and self.current_state == "idle"
            and (now - self.last_cursor_move_time < 2.5)
        ):
            pet_center_x = self.x() + int((FRAME_WIDTH * self.scale) / 2)
            pet_center_y = self.y() + 80 + int((FRAME_HEIGHT * self.scale) / 2)
            dx = cursor_pos.x() - pet_center_x
            dy = cursor_pos.y() - pet_center_y
            dist = math.hypot(dx, dy)

            if dist > 50:  # Deadzone
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

        # 3. Autonomes Roaming am Desktop-Rand
        if self.roaming_enabled and not self.dragging and not self.one_shot_active and self.current_state == "idle":
            if now > self.next_roam_decision:
                r = random.random()
                if r < 0.45:
                    self.roam_direction = "left"
                    self.roam_end_time = now + random.uniform(1.8, 3.5)
                elif r < 0.90:
                    self.roam_direction = "right"
                    self.roam_end_time = now + random.uniform(1.8, 3.5)
                else:
                    self.roam_direction = "idle"
                    self.roam_end_time = now + random.uniform(2.0, 4.0)
                self.next_roam_decision = self.roam_end_time + random.uniform(3.0, 6.0)

            if now < self.roam_end_time and self.roam_direction != "idle":
                screen = QApplication.primaryScreen()
                if screen:
                    geom = screen.availableGeometry()
                    speed = 2
                    cur_x = self.x()
                    min_x = geom.left() + 20
                    max_x = geom.right() - int(FRAME_WIDTH * self.scale) - 20

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

    def paintEvent(self, event):
        if self.spritesheet.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        now = time.time()

        # 1. Sprechblase zeichnen (falls aktiv)
        if self.speech_enabled and self.speech_bubble_text and now < self.speech_bubble_expire:
            font = QFont("sans-serif", 9, QFont.Weight.Bold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(self.speech_bubble_text) + 24
            bubble_width = min(280, max(120, text_width))
            bubble_height = 36

            bubble_x = max(10, int((self.width() - bubble_width) / 2))
            bubble_y = 15

            # Hintergrund
            painter.setBrush(QBrush(QColor(10, 15, 25, 220)))
            painter.setPen(QPen(QColor(0, 212, 255, 200), 1.5))
            painter.drawRoundedRect(QRectF(bubble_x, bubble_y, bubble_width, bubble_height), 10, 10)

            # Pfeil nach unten zum Pet
            arrow_x = int(self.width() / 2)
            arrow_y = bubble_y + bubble_height
            arrow_pts = [
                QPoint(arrow_x - 6, arrow_y),
                QPoint(arrow_x + 6, arrow_y),
                QPoint(arrow_x, arrow_y + 6)
            ]
            painter.drawPolygon(arrow_pts)

            # Text
            painter.setPen(QColor(220, 245, 255))
            painter.drawText(
                QRect(bubble_x + 6, bubble_y, bubble_width - 12, bubble_height),
                Qt.AlignmentFlag.AlignCenter,
                self.speech_bubble_text
            )

        # 2. Sprite Frame bestimmen
        state = self.current_state

        # Roaming Animations-Override
        if self.roaming_enabled and not self.dragging and not self.one_shot_active and now < self.roam_end_time and self.roam_direction != "idle":
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

        # 3. Sprite zeichnen
        sx = source_col * FRAME_WIDTH
        sy = source_row * FRAME_HEIGHT

        target_w = int(FRAME_WIDTH * self.scale)
        target_h = int(FRAME_HEIGHT * self.scale)
        target_x = int((self.width() - target_w) / 2)
        target_y = 70  # Unterhalb der Sprechblasen-Zone

        painter.drawImage(
            QRect(target_x, target_y, target_w, target_h),
            self.spritesheet,
            QRect(sx, sy, FRAME_WIDTH, FRAME_HEIGHT)
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WebJarvis Desktop Pet")

    script_dir = Path(__file__).resolve().parent
    spritesheet_path = script_dir / "pets" / "yuyu-chibi" / "spritesheet.webp"

    # Fallback Pfad
    if not spritesheet_path.exists():
        spritesheet_path = Path("/home/graba/Schreibtisch/ASGRAD/Valhalla/TOOLS/GRABAS_GITHUB/webjarvis_petaddon/pets/yuyu-chibi/spritesheet.webp")

    pet = DesktopPetWindow(str(spritesheet_path))
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
