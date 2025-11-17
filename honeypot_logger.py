# \# honeypot_logger.py
"""
Honeypot logger: subscribes to all topics and logs everything.
Writes logs to 'mqtt_messages.log' (plain text), 'mqtt_messages.csv' (CSV),
and inserts attack logs into SQLite database.
"""

import csv
import datetime
import os
import re
from paho.mqtt import client as mqtt
import alert_handler

from database import insert_attack, init_db   # <-- correct import

BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "HoneypotLogger-01"
LOG_CSV = "mqtt_messages.csv"
LOG_TXT = "mqtt_messages.log"

SUSPICIOUS_PATTERNS = [
    re.compile(r"hack", re.IGNORECASE),
    re.compile(r"exploit", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"admin", re.IGNORECASE)
]

def ensure_csv_header():
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "topic", "payload", "qos", "retain"])

def classify_attack(payload):
    """Simple keyword-based attack detector."""
    for patt in SUSPICIOUS_PATTERNS:
        if patt.search(payload):
            return "suspicious"
    return "normal"

def log_message(topic, payload, qos, retain):
    ts = datetime.datetime.utcnow().isoformat()

    # 1️⃣ Log to text file
    with open(LOG_TXT, "a", encoding="utf-8") as ftxt:
        ftxt.write(f"{ts} | {topic} | {payload}\n")

    # 2️⃣ Log to CSV
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ts, topic, payload, qos, retain])

    # 3️⃣ Determine attack type
    attack_type = classify_attack(payload)

    # 4️⃣ Insert into database
    ip_address = "unknown"  # If you want real IP later, I can add code
    insert_attack(ts, topic, payload, ip_address, attack_type)

    # 5️⃣ Trigger alert if suspicious
    if attack_type == "suspicious":
        alert_handler.handle_alert(topic, payload, ts)

def on_connect(client, userdata, flags, rc):
    print(f"[logger] connected (rc={rc}), subscribing to all topics (#)")
    client.subscribe("#")

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors='ignore')
    print(f"[logger] {msg.topic} => {payload}")
    log_message(msg.topic, payload, msg.qos, msg.retain)

def main():
    init_db()              # <-- IMPORTANT: create DB table
    ensure_csv_header()
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()

if __name__ == "__main__":
    main()
