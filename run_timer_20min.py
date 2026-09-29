#!/usr/bin/env python3
import time
import os
import sys
import subprocess
from datetime import datetime, timedelta

DURATION_SECONDS = 20 * 60 # 20 Minuten
LOG_FILE = "/tmp/timer_20min.log"
PID_FILE = "/tmp/timer_20min.pid"
SOUND_FILE = "/home/graba/Schreibtisch/ASGRAD/universfield-new-notification-026-380249.mp3"

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
        f.flush()
    print(line, end="", flush=True)

def notify(msg):
    try:
        subprocess.run(["notify-send", "-a", "Yuyu Tamagotchi Timer", "⏳ 20-Minuten Entwicklungs-Timer", msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

start_time = time.time()
end_time = start_time + DURATION_SECONDS
target_str = datetime.fromtimestamp(end_time).strftime('%H:%M:%S')

with open(LOG_FILE, "w") as f:
    f.write(f"=== 20-MINUTEN TIMER GESTARTET (Ziel: {target_str}) ===\n")

log(f"Timer gestartet! 20 Minuten (bis {target_str})")
notify(f"20 Minuten Sprint gestartet!\nEnde: {target_str}")

notified_milestones = set()

while True:
    now = time.time()
    remaining = int(end_time - now)
    if remaining <= 0:
        break
    
    mins = remaining // 60
    secs = remaining % 60
    
    # Meilensteine bei 15m, 10m, 5m, 1m
    if mins in (15, 10, 5, 1) and secs == 0 and mins not in notified_milestones:
        notified_milestones.add(mins)
        log(f"⏱️ Noch {mins} Minuten verbleibend...")
        notify(f"Noch {mins} Minuten verbleibend!")
        
    if remaining % 60 == 0:
        log(f"Verbleibend: {mins:02d}:{secs:02d}")
        
    time.sleep(1)

log("🎉 20 MINUTEN ABGELAUFEN! Sprint beendet!")
notify("🎉 20 Minuten abgelaufen! Sprint abgeschlossen!")

if os.path.exists(SOUND_FILE):
    subprocess.run(["pw-play", SOUND_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if os.path.exists(PID_FILE):
    try:
        os.remove(PID_FILE)
    except Exception:
        pass
