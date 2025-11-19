import paho.mqtt.client as mqtt
import time
from collections import deque
import json

BROKER = "broker.hivemq.com"
PORT = 1883

CONTROL_TOPIC = "door/lock/control"
STATE_TOPIC = "door/lock/state"

timestamps = deque(maxlen=20)
ALERT_COOLDOWN = 3
last_alert = 0

def alert(message):
    global last_alert
    if time.time() - last_alert > ALERT_COOLDOWN:
        print(message)
        last_alert = time.time()

def on_connect(client, userdata, flags, rc):
    print("[DETECTOR] Connected:", rc)
    client.subscribe("door/lock/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"[LOG] {topic} -> {payload}")

    # ======================================================================
    # HANDLE CONTROL TOPIC (where commands arrive)
    # ======================================================================
    if topic == CONTROL_TOPIC:

        # ---- STEP 1: Try to parse JSON ----
        try:
            data = json.loads(payload)
        except:
            alert("[ALERT] 🚨 Invalid JSON → Attack detected!")
            return

        # ---- STEP 2: Check required fields ----
        if "user" not in data or "pass" not in data or "cmd" not in data:
            alert("[ALERT] 🚨 Missing credentials → Attack detected!")
            return

        # ---- STEP 3: Validate credentials ----
        if data["user"] == "iotgroup" and data["pass"] == "doorlock":
            # Valid remote user → NO alert
            print("[DETECTOR] Authorized remote user command")
            return

        # ---- STEP 4: Credentials wrong → attacker ----
        alert("[ALERT] 🚨 Unauthorized control command detected!")

        # ---- STEP 5: Flood attack detection ----
        now = time.time()
        timestamps.append(now)

        if len(timestamps) >= 3 and (timestamps[-1] - timestamps[-3] < 3.0):
            alert("[ALERT] 🚨 Flood attack detected!")

        return

    # ======================================================================
    # HANDLE STATE MESSAGES (normal)
    # ======================================================================
    if topic == STATE_TOPIC:
        # These are legitimate device updates
        return


# ======================================================================
# MQTT CLIENT INITIALIZATION
# ======================================================================
client = mqtt.Client("detector_engine")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
