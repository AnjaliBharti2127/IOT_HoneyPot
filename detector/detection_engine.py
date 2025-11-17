import time
import os
import re
from collections import deque

LOG_FILE = "/opt/homebrew/var/log/mosquitto/mosquitto.log"
CONTROL_KEYWORD = "/control"

control_timestamps = deque(maxlen=30)

last_alert_time = 0        # NEW: global cooldown timer
ALERT_COOLDOWN = 3         # seconds

# ----------------------------------------------------
# macOS Beep
# ----------------------------------------------------
def beep_alert():
    print("[ALERT SOUND] Playing macOS ping sound...")
    os.system("afplay /System/Library/Sounds/Ping.aiff &")
    time.sleep(0.7)
    os.system("afplay /System/Library/Sounds/Ping.aiff &")
    time.sleep(0.7)
    os.system("afplay /System/Library/Sounds/Ping.aiff &")

# ----------------------------------------------------
# Log Tail
# ----------------------------------------------------
def tail_log(path):
    print("[DETECTOR] Monitoring log file:", path)
    with open(path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            if "Received PUBLISH" in line:
                process_control(line)

# ----------------------------------------------------
# Control Processor
# ----------------------------------------------------
def process_control(line):
    if CONTROL_KEYWORD not in line:
        return

    print("[LOG] CONTROL message received:", line.strip())

    now = time.time()
    control_timestamps.append(now)

    detect_flood()

# ----------------------------------------------------
# Flood Detection with Cooldown
# ----------------------------------------------------
def detect_flood():
    global last_alert_time

    if len(control_timestamps) < 3:
        return

    # If last 3 messages arrived within 1.5 seconds → flood
    if control_timestamps[-1] - control_timestamps[-3] < 1.5:

        # COOLDOWN: Only alert if last alert was >3 sec ago
        if time.time() - last_alert_time > ALERT_COOLDOWN:
            print("[ALERT] 🚨 Rapid control flood detected! Possible attack.")
            beep_alert()
            last_alert_time = time.time()  # Reset cooldown timer

# ----------------------------------------------------
# Main
# ----------------------------------------------------
def main():
    if not os.path.exists(LOG_FILE):
        print("[DETECTOR] Log file not found:", LOG_FILE)
        return

    print("[DETECTOR] Starting Detection Engine with Cooldown...")
    tail_log(LOG_FILE)

if __name__ == "__main__":
    main()
