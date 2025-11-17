import paho.mqtt.client as mqtt
import time
from collections import deque
import os

BROKER = "broker.hivemq.com"
PORT = 1883

CONTROL_TOPIC = "door/lock/control"
STATE_TOPIC = "door/lock/state"

timestamps = deque(maxlen=20)
ALERT_COOLDOWN = 3
last_alert = 0

def beep_alert():
    os.system("afplay /System/Library/Sounds/Ping.aiff &")
    time.sleep(0.6)
    os.system("afplay /System/Library/Sounds/Ping.aiff &")
    time.sleep(0.6)
    os.system("afplay /System/Library/Sounds/Ping.aiff &")

def alert(message):
    global last_alert
    if time.time() - last_alert > ALERT_COOLDOWN:
        print(message)
        beep_alert()
        last_alert = time.time()

def on_connect(client, userdata, flags, rc):
    print("[DETECTOR] Connected:", rc)
    client.subscribe("door/lock/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"[LOG] {topic} -> {payload}")

    # 1) Unauthorized control message (device never sends control)
    if topic == CONTROL_TOPIC:
        alert("[ALERT] 🚨 Unauthorized control command detected!")
        # also check for flood
        now = time.time()
        timestamps.append(now)

        # flood (3 msgs < 1.5 sec)
        if len(timestamps) >= 3 and (timestamps[-1] - timestamps[-3] < 1.5):
            alert("[ALERT] 🚨 Flood attack detected!")
        return

    # 2) State messages are normal
    if topic == STATE_TOPIC:
        # Do nothing (legitimate)
        return

client = mqtt.Client("detector_engine")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
