# alert_handler.py
"""
Alert actions: write an alert CSV and emit a beep (Windows).
"""

import csv
import datetime
import os
import sys

ALERT_CSV = "alerts.csv"

def ensure_alert_header():
    if not os.path.exists(ALERT_CSV):
        with open(ALERT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp","topic","payload"])

def handle_alert(topic, payload, ts=None):
    if ts is None:
        ts = datetime.datetime.utcnow().isoformat()
    ensure_alert_header()
    with open(ALERT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ts, topic, payload])
    print(f"[ALERT] {ts} | {topic} | {payload}")

    # Beep on Windows
    if sys.platform.startswith("win"):
        try:
            import winsound
            winsound.Beep(1000, 300)  # frequency, duration(ms)
        except Exception:
            pass
